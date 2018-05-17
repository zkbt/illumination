from ..imports import *
from ..cosmics.stamps import Stamp


class Sequence(Talker):
	'''
	A sequence of one or more images,
	which can be viewed (and animated)
	in a tv frame.
	'''
	def __init__(self, *args, **kwargs):
		Talker.__init__(self)

	def _findtimestep(self, time):
		'''
		Given a time, identify its index.
		'''
		try:
			return np.flatnonzero(self._gettimes() <= time)[-1]
		except IndexError:
			return 0

	def _gettimes(self):
		'''
		Get the available times associated with this frame.
		'''
		return self.time

class FITS_Sequence(Sequence):

	def __init__(self, initial, ext_image=1, ext_primary=0):
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
		Sequence.__init__(self)

		self.hdulists = []

		# we want to make a list of HDULists
		if type(initial) == fits.HDUList:
			self.hdulists = [initial]
		elif type(initial) == str:
			# a search string
			if '*' in initial:
				self.hdulists = [fits.open(f) for f in glob.glob(initial)]
			# a single file
			elif 'fit' in initial.lower():
				self.hdulists = [fits.open(initial)]
		elif type(initial) == list:
			# a list of filenames
			if np.all([type(s) == str for s in initial]):
				if np.all(['fit' in f.lower() for f in initial]):
					self.hdulists = [fits.open(f) for f in initial]
			elif np.all([type(hdu) == fits.HDUList for hdu in initial]):
				self.hdulists = initial


		self.ext_primary = ext_primary
		self.ext_image = ext_image

		self.temporal = {}
		self.static = {}
		self.spatial = {}

		self._populate_from_headers()

	@property
	def N(self):
		return len(self.hdulists)

	@property
	def filenames(self):
		return [h.filename() for h in self.hdulists]

	def _populate_from_headers(self):
		'''
		Attempt to populate the sequence from the headers.
		'''

		first = self.hdulists[0]
		pri, img = first[self.ext_primary].header, first[self.ext_image].header


		# if only a single image, everything is static (but can be viewed as temporal)

		if len(self.hdulists) == 1:
			both = fits.HeaderDiff(pri, img)

			for k in both.common_keywords:
				self.static[k] = img[k]
			for k, v in zip(both.diff_keywords, both.diff_keyword_values):
				self.static[k] = v
			self.temporal = self.static
		else:
			extensions = np.unique([self.ext_primary, self.ext_image])
			for e in extensions:
				h = first[e].header
				for k in h.keys():
					self.temporal[k] = []

			# compile all values from the headers
			for hdulist in self.hdulists:
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
				self.time = self.temporal[k]
				self.speak('using {} as the time axis'.format(k))
				break
			except KeyError:
				pass


class StampSequence(Sequence):
	def __init__(self, stamp):
		for k in stamp._savable:
			vars(self)[k] = vars(stamp)[k]


def make_sequence(initial):
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

	# a Stamp?
	if type(initial) == Stamp:
		return StampSequence(initial)
	else:
		return FITS_Sequence(initial)


def test(ext_image=0,
		 pattern='/Users/zkbt/Dropbox/TESS/may-visit/simulated/ffi/1800s/ccd1/simulated_18h00m00s+66d33m39s_ccd1_*.fits'):

	a = FITS_Sequence(pattern, ext_image=ext_image)
	files = glob.glob(pattern)
	b = FITS_Sequence(files, ext_image=ext_image)
	c = FITS_Sequence([fits.open(f) for f in files], ext_image=ext_image)
	d = FITS_Sequence(files[0], ext_image=ext_image)
	e = FITS_Sequence(fits.open(files[0]), ext_image=ext_image)

	for x in [a,b,c,d,e]:
		print(x, x.N)
	return a,b,c,d,e
