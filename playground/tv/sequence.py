from ..imports import *
from ..postage.stamps import Stamp
from ..postage.tpf import EarlyTessTargetPixelFile
from lightkurve.lightcurve import LightCurve
from lightkurve.targetpixelfile import TargetPixelFile

timescale = 'tdb'
# by default, assume all times are TDB
# this is ahead of TAI by about 31.184s
# and it differs from UTC by additional leap seconds

def guess_time_format(t, default='jd'):
	'''
	For a given array of times,
	make a guessa about its time format.
	'''
	ranges = dict(	gps=[0.1e9, 2e9], # valid between 1983-03-08 09:46:59.000 and 2043-05-23 03:33:39.000
					jd=[2.4e6, 3e6], # valid between 1858-11-16 12:00:00.000 and 3501-08-15 12:00:00.000
					mjd=[4e4, 8e4]) # valid between 1968-05-24 00:00:00.000 and 2077-11-28 00:00:00.000

	if t == []:
		return default

	for k in ranges.keys():
		if np.min(t) >= ranges[k][0] and np.max(t) <= ranges[k][1]:
			return k

	return default

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
		'''

		Returns
		-------

		'''

		return np.median(np.diff(self.time))

	def _find_timestep(self, time):
		'''
		Given a time, identify its index.

		Parameters
		----------

		time : float
			A single time (in JD?).

		Returns
		-------
		index : int
			The index of the *closest* time point.
		'''

		# pull out actual times associated with this sequence
		times = self._gettimes()

		# if there are no times, return nothing
		if len(times) == 0:
			return None
		else:
			# find the index of the timepoint that is closest to this one
			diff = time - times
			step = np.argmin(abs(diff))
			return step

	def _gettimes(self):
		'''
		Get the available times associated with this frame.

		Returns
		-------
		times : array
			All of the times associated with this sequence.
		'''
		return self.time

	def __repr__(self):
		'''
		How should this sequence be represented, by default, as a string.
		'''
		return '<{} of {} images>'.format(self.nametag, self.N)

	@property
	def N(self):
		'''
		How many elements are in this sequence?
		'''
		return len(self.time)

class FITS_Sequence(Sequence):
	'''
	A sequence of FITS images, with a time associated with each.
	'''
	def __init__(self, initial, ext_image=1, ext_primary=0, name='FITS', **kwargs):
		'''
		Initialize a Sequence of FITS images. The goal is
		to create a list of FITS HDUs, one for each time.


		Parameters
		----------
		initial : (many possible types)
			-single FITS filename, and an extension to use.
			-list of FITS filenames, and an extension to use.
			-a glob-like search string containing '*'.
			-single FITS HDUList, and an extension to use.
			-list of loaded FITS HDULists, and an extension to use.
		'''

		# initialize the basic sequence
		Sequence.__init__(self, name=name)

		# we keep the HDUs out of memory, until we need them
		# (this should probably someday be rewritten as an iterator?)
		self._hdulists = None

		# ultimately, we want to make a list of filenames or HDULists
		if type(initial) == fits.HDUList:
			# if this is one HDUList, make it a list of them
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
			if np.all([os.path.exists(s) for s in initial]):
				self.filenames = initial
			elif np.all([type(hdu) == fits.HDUList for hdu in initial]):
				self._hdulists = initial

		# if we're starting frmo hdulists, then get their filenames
		if self._hdulists is not None:
			self.filenames = [h.filename() for h in self._hdulists]

		# make sure this FITS_Sequence isn't empty
		assert(len(self.filenames) > 0)

		self.ext_primary = ext_primary
		self.ext_image = ext_image
		#if len(self.hdulists) > 0:
		#	self.ext_image = np.minimum(self.ext_image, len(self.hdulists[0]))

		self.temporal = {}
		self.static = {}
		self.spatial = {}

		# make up an imaginary GPS time (and keep track of whether it is fake)
		self.time = Time(np.arange(self.N), format='gps', scale='tai')
		self._timeisfake = True
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

		(We might want to open them only one at a time, for memory's sake.)
		'''
		if self._hdulists is not None:
			return self._hdulists[i]
		else:
			return fits.open(self.filenames[i], memmap=False)

	def _populate_from_headers(self, timeformat=None):
		'''
		Attempt to populate the sequence from the headers.
		'''

		# pull out the first HDUList in the sequence
		first = self._get_hdulist(0)

		# check to see if the requested image extension exists
		try:
			first[self.ext_image]
		except IndexError:
			print('image extension {} not found, switching to 0'.format(self.ext_image))
			self.ext_image = 0

		# load the headers for the primary and the image
		pri, img = first[self.ext_primary].header, first[self.ext_image].header

		# if only a single image, everything is static (but can be viewed as temporal)
		if self.N == 1:
			for h in [pri, img]:
				for k in h.keys():
					self.static[k] = h[k]
					self.temporal[k] = [self.static[k]]
		else:

			# look through the unique extensions
			extensions = np.unique([self.ext_primary, self.ext_image])

			# create lists for each key in the headers
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
				# treat some value as a time
				t = self.temporal[k]

				# if it's already an astropy time, keep it as such
				if isinstance(t, Time):
					self.time = t
				# make an astropy time out of the values
				else:
					self.time = Time(np.asarray(t), format=timeformat or guess_time_format(t), scale=timescale)
				self.speak('using {} as the time axis'.format(k))
				self._timeisfake = False
			except KeyError:
				break

	def __getitem__(self, timestep):
		'''
		Return the image data for a given timestep.

		Parameters
		----------
		timestep : int
			An index for a timestep.
		'''
		if timestep is None:
			return None
		else:
			return self._get_hdulist(timestep)[self.ext_image].data



class Stamp_Sequence(Sequence):
	def __init__(self, initial, name='Stamp', **kwargs):
		'''
		Initialize a Sequence from a Stamp.
		(a Stamp is a custom, simplified version of a TPF)

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

		# (not coincidentally), a Stamp has similar variables to a Sequence
		for k in stamp._savable:
			vars(self)[k] = vars(stamp)[k]

		# set up the basic sequence, including the time array
		self.stamp = stamp
		if isinstance(self.stamp.time, Time):
			self.time = self.stamp.time
		else:
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



class Timeseries_Sequence(Sequence):
	'''
	NOT CURRENTLY BEING USED.
	'''
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
		#try:
		#	# is initial a 1D thing?
		#	assert(len(np.shape(initial))==1 or isinstance(initial, LightCurve))
		#	return Timeseries_Sequence(initial, *args, **kwargs)
		#except AssertionError:
		try:
			assert(isinstance, TargetPixelFile)
			return TPF_Sequence(initial, *args, **kwargs)
		except (AttributeError,AssertionError):
			return FITS_Sequence(initial, *args, **kwargs)
