from ..imports import *
from ..cosmics.stamps import Stamp, create_test_stamp
from .utils import create_test_fits

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
		try:
			step = np.flatnonzero(np.abs(diff)<=(self.cadence()/2.0))
			assert(len(step) == 1)
			return step[0]
		except (IndexError, AssertionError):
			return 0

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

		self.time = np.arange(self.N)
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
			return self._hdulists[0]
		else:
			return fits.open(self.filenames[i])

	def _populate_from_headers(self):
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
				self.time = np.asarray(self.temporal[k])
				self.speak('using {} as the time axis'.format(k))
			except KeyError:
				break

	def __getitem__(self, timestep):
		'''
		Return the image data for a given timestep.
		'''
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
		self.time = self.stamp.time

	def __getitem__(self, timestep):
		'''
		Return the image data for a given timestep.
		'''
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
		return FITS_Sequence(initial, *args, **kwargs)

def test_Stamps():
	'''
	Run a test of Stamps_Sequence
	'''

	filename = 'temporarystamp.npy'
	stamp = create_test_stamp()
	stamp.save(filename)
	a = Stamp_Sequence(stamp)
	b = Stamp_Sequence(filename)
	return a, b

def test_FITS():
	'''
	Run a test of the FITS_Sequence.
	'''
	filename = 'temporarytest.fits'
	pattern = 'tempo*arytest.fits'
	hdulist = create_test_fits()
	hdulist.writeto(filename, overwrite=True)
	ext_image = 1

	a = FITS_Sequence(pattern, ext_image=ext_image)
	files = glob.glob(pattern)
	b = FITS_Sequence(files, ext_image=ext_image)
	c = FITS_Sequence(hdulist, ext_image=ext_image)
	d = FITS_Sequence(filename, ext_image=ext_image)
	e = FITS_Sequence([hdulist], ext_image=ext_image)

	return a,b,c,d,e

def test_many_FITS(N=30):
	'''
	Run a test of the FITS_Sequence.
	'''

	mkdir()
	for i in range(N):

		filename = 'temporarytest_{:04}.fits'.format(i)
		pattern = 'temporarytest_*.fits'
		hdulist = create_test_fits(rows=4, cols=6)
		hdulist.writeto(filename, overwrite=True)
		ext_image = 1
		print('saved {}'.format(filename))
		a = FITS_Sequence(pattern, ext_image=ext_image)

	return a
