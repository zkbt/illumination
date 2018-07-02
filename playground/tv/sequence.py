from ..imports import *
from ..postage.stamps import Stamp
from ..postage.tpf import EarlyTessTargetPixelFile
from lightkurve.lightcurve import LightCurve
from lightkurve.targetpixelfile import TargetPixelFile

timescale = 'tdb'
# by default, assume all times are TDB
# this is ahead of TAI by about 31.184s
# and it differs from UTC by additional leap seconds

def guess_time_format(t):
	'''
	For a given array of times,
	make a guessa about its time format.
	'''
	ranges = dict(	gps=[0.1e9, 2e9], # valid between 1983-03-08 09:46:59.000 and 2043-05-23 03:33:39.000
					jd=[2.4e6, 3e6], # valid between 1858-11-16 12:00:00.000 and 3501-08-15 12:00:00.000
					mjd=[4e4, 8e4]) # valid between 1968-05-24 00:00:00.000 and 2077-11-28 00:00:00.000

	for k in ranges.keys():
		if np.min(t) >= ranges[k][0] and np.max(t) <= ranges[k][1]:
			return k

	return None

class Sequence(Talker):
	'''
	A sequence of one or more images,
	which can be viewed (and animated)
	in a tv frame.
	'''

	titlefordisplay = ''
	colorbarlabelfordisplay = ''
	def __init__(self, name='generic', *args, **kwargs):
		Talker.__init__(self)
		self.name = name

	def cadence(self):
		return np.median(np.diff(self.time))

	def _find_timestep(self, time):
		'''
		Given a time, identify its index.
		'''

		diff = time - self._gettimes()
		if len(diff) == 0:
			return None
		else:
			step = np.argmin(abs(diff))
			return step
		#try:
			#step = np.argmin(abs(diff))#
			#step = np.flatnonzero(abs(diff)<=(self.cadence()/2.0))
			#print(self.cadence())
			#assert(len(step) == 1)
			#return step[0]
		#except (IndexError, AssertionError):
		#	return 0

	def _gettimes(self):
		'''
		Get the available times associated with this frame.
		'''
		return self.time

	def __repr__(self):
		return '<{} of {} images>'.format(self.nametag, self.N)


class FITS_Sequence(Sequence):

	def __init__(self, initial, ext_image=1, ext_primary=0, name='FITS', **kwargs):
		'''
		Initialize a Sequence of FITS images. The goal is
		to create a list of FITS HDUs, one for each time.


		Parameters
		----------
		initial : (many possible types)
			-single FITS filename, and an extension to use.
			-list of FITS filenames, and an extension to use.
			-a glob-like search string containing '*'
			-single FITS HDUList, and an extension to use.
			-list of loaded FITS HDULists, and an extension to use.

		'''
		Sequence.__init__(self, name=name)

		# we keep the HDUs out of memory, until we need them
		# (this should probably be rewritten as an iterator?)
		self._hdulists = None

		# we want to make a list of HDULists
		if type(initial) == fits.HDUList:
			self._hdulists = [initial]
		elif type(initial) == str:
			# a search string
			if '*' in initial:
				self.filenames = glob.glob(initial)
				#self.hdulists = [fits.open(f) for f in glob.glob(initial)]
			# a single file
			elif 'fit' in initial.lower():
				self.filenames = [initial]
				#self.hdulists = [fits.open(initial)]
		elif type(initial) == list:
			# a list of filenames
			if np.all([type(s) == str for s in initial]):
				if np.all(['fit' in f.lower() for f in initial]):
					self.filenames = initial
					#self.hdulists = [fits.open(f) for f in initial]
			elif np.all([type(hdu) == fits.HDUList for hdu in initial]):
				self._hdulists = initial

		# if we're starting frmo hdulists, then get their filenames
		if self._hdulists is not None:
			self.filenames = [h.filename() for h in self._hdulists]

		self.ext_primary = ext_primary
		self.ext_image = ext_image
		#if len(self.hdulists) > 0:
		#	self.ext_image = np.minimum(self.ext_image, len(self.hdulists[0]))

		self.temporal = {}
		self.static = {}
		self.spatial = {}

		# make up an imaginary GPS time
		self.time = Time(np.arange(self.N), format='gps', scale=timescale)
		try:
			self._populate_from_headers()
		except:
			self.speak('unable to populate headers for {}'.format(self))

	@property
	def N(self):
		'''
		How many elements are in this sequence?
		'''
		return len(self.filenames)

	def _get_hdulist(self, i):
		'''
		Return an HDUlist for the ith element in the sequence.
		'''
		if self._hdulists is not None:
			return self._hdulists[i]
		else:
			return fits.open(self.filenames[i], memmap=False)

	def _populate_from_headers(self, timeformat=None):
		'''
		Attempt to populate the sequence from the headers.
		'''

		first = self._get_hdulist(0)
		try:
			first[self.ext_image]
		except IndexError:
			print('image extension {} not found, switching to 0'.format(self.ext_image))
			self.ext_image[0]

		pri, img = first[self.ext_primary].header, first[self.ext_image].header

		# if only a single image, everything is static (but can be viewed as temporal)

		if self.N == 1:
			for h in [pri, img]:
				for k in h.keys():
					self.static[k] = h[k]
					self.temporal[k] = [self.static[k]]
		else:
			extensions = np.unique([self.ext_primary, self.ext_image])
			for e in extensions:
				h = first[e].header
				for k in h.keys():
					self.temporal[k] = []

			# compile all values from the headers
			for i in range(self.N):
				hdulist = self._get_hdulist(i)
				for e in extensions:
					h = hdulist[e].header
					for k in h.keys():
						self.temporal[k].append(h[k])

			# move non-changing things to static
			for k in list(self.temporal.keys()):
				if len(np.unique(self.temporal[k])) == 1:
					self.static[k] = self.temporal.pop(k)[0]


		# try to pull a time axis from these
		for k in ['TIME', 'MJD', 'JD', 'BJD', 'BJD_TDB']:
			try:
				t = self.temporal[k]
				self.time = Time(np.asarray(t), format=timeformat or guess_time_format(t), scale=timescale)
				self.speak('using {} as the time axis'.format(k))
			except KeyError:
				break

	def __getitem__(self, timestep):
		'''
		Return the image data for a given timestep.
		'''
		if timestep is None:
			return None
		else:
			return self._get_hdulist(timestep)[self.ext_image].data


class Stamp_Sequence(Sequence):
	def __init__(self, initial, name='Stamp', **kwargs):
		'''
		Initialize a Sequence from a Stamp.


		Parameters
		----------
		initial : (many possible types)
			-a single Stamp object
			-something that can initialize a Stamp
				A filename for a '.npy' file.
				A list of FITS sparse_subarray files.
				A search path of FITS sparse_subarray files (e.g. containing *.fits)

		**kwargs : dict
			Keyword arguments are passed to Stamp(initial, **kwargs)
		'''

		# make sure we have at least a stamp
		if type(initial) == Stamp:
			stamp = initial
		elif (type(initial) == str) or (type(initial) == list):
			stamp = Stamp(initial, **kwargs)

		# create a sequence out of that stamp
		Sequence.__init__(self, name=name)
		for k in stamp._savable:
			vars(self)[k] = vars(stamp)[k]

		# set up the basic sequence
		self.stamp = stamp
		self.time = Time(self.stamp.time, format=guess_time_format(self.stamp.time), scale=timescale)

	def __getitem__(self, timestep):
		'''
		Return the image data for a given timestep.
		'''
		if timestep is None:
			return None
		else:
			return self.stamp.todisplay[timestep, :, :]

	@property
	def N(self):
		return len(self.time)

	@property
	def titlefordisplay(self):
		return self.stamp.titlefordisplay

	@property
	def colorbarlabelfordisplay(self):
		return self.stamp.colorbarlabelfordisplay

class TPF_Sequence(Sequence):
	def __init__(self, initial, name='TPF', **kwargs):
		'''
		Initialize a Sequence from a Target Pixel File
		(see lightkurve).


		Parameters
		----------
		initial :
			-a TargetPixelFile object
			-a filename of a TargetPixelFile

		**kwargs : dict
			Keyword arguments are stored in self.keywords.
		'''


		# make sure we have a TPF as imput
		if type(initial) == str:
			tpf = EarlyTessTargetPixelFile.from_fits(initial)
		else:
			tpf = initial

		# create a sequence out of that stamp
		Sequence.__init__(self, name=name)

		# set up the basic sequence
		self.tpf = tpf
		self.time = Time(self.tpf.time, format='jd', scale=timescale)
		self.titlefordisplay = 'TIC{}\nCAM{} | ({},{}) | {:.0f}s'.format(tpf.tic_id, tpf.cam, tpf.col_cent, tpf.row_cent, tpf.cadence.to('s').value)

	def __getitem__(self, timestep):
		'''
		Return the image data for a given timestep.
		'''
		if timestep is None:
			return None
		else:
			return self.tpf.flux[timestep, :, :]

	@property
	def N(self):
		return len(self.time)

class Timeseries_Sequence(Sequence):
	def __init__(self, initial, y=None, yuncertainty=None, name='timeseries', **kwargs):
		'''
		Initialize a Sequence from some 1D timeseries.

		Parameters
		----------
		initial : LightCruve object, or array of times (either astropy times, or in JD)
			The time values, to be plotted on the x-axis
		y : array
			The values to be plotted on the y-axis
		yuncertainty : array
			The errorbars on y (optional).
		**kwargs are passed to plt.plot()
		'''

		try:
			# is it a lightkurve?
			time = initial.time
			y = initial.flux
		except:
			time = initial

		# make sure we have a TPF as imput
		# set up the basic sequence
		if isinstance(time, Time):
			self.time = time
		else:
			self.time = Time(time, format=guess_time_format(time), scale=timescale)

		# store the dependent values
		self.y = y
		self.yuncertainty = yuncertainty

		# create a sequence out of that stamp
		Sequence.__init__(self, name=name)
		cadence = np.round(np.median(np.diff(self.time)).to('s').value)

		# set a rough title for this plot
		self.titlefordisplay = '{}'.format(self.name)

	def __getitem__(self, timestep):
		'''
		Return the image data for a given timestep.
		'''
		if timestep is None:
			return None
		else:
			return self.y[timestep, :, :]

	@property
	def N(self):
		return len(self.time)


def make_sequence(initial, *args, **kwargs):
	'''
	Initialize a Sequence for viewing with tv.


	Parameters
	-----------
	initial : (many possible types)
		This is the input that initializes an image sequence.
			-single FITS filename, and an extension to use.
			-list of FITS filenames, and an extension to use.
			-single FITS HDUList, and an extension to use.
			-list of loaded FITS HDULists, and an extension to use.
			-a Stamp object from the `cosmics` package.

	'''

	if issubclass(initial.__class__, Sequence):
		return initial
	elif type(initial) == Stamp:
		return Stamp_Sequence(initial, *args, **kwargs)
	else:
		try:
			# is initial a 1D thing?
			assert(len(np.shape(initial))==1 or isinstance(initial, LightCurve))
			return Timeseries_Sequence(initial, *args, **kwargs)
		except AssertionError:
			try:
				assert(isinstance, TargetPixelFile)
				return TPF_Sequence(initial, *args, **kwargs)
			except AssertionError:
				return FITS_Sequence(initial, *args, **kwargs)
