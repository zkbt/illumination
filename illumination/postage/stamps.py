'''
This constructs a stamp, as a Cube, from a directory of
sparse_subaray files.
'''

from ..imports import *
from .cubes import Cube
from astropy.time import Time
from lightkurve.targetpixelfile import TargetPixelFile

class Stamp(Cube):
	"""
	TESS postage stamp. Similar to a lightweight version of lightkurve.
	"""

	def __init__(self, path=None, extension=1, limit=None,
				 photons=None, spatial={}, static={}, temporal={}, **kw):
		'''
		Basically a light-weight version of a TPF.

		Parameters
		----------
		path : str, list of strings, list of HDULists, a TPF object
			A filename for a '.npy' file.
			A list of FITS sparse_subarray files.
			A search path of FITS sparse_subarray files (e.g. containing *.fits)
		extension : int
			Which stamp to pull from the subarray?
		limit : int
			How many files (in the search path) should we stop at?
		cube_kw : dict
			The inputs for a Cube.
		'''

		# figure out how to load the stamp
		if photons is not None:
			Cube.__init__(self, photons=photons, spatial=spatial, static=static, temporal=temporal)
		else:
			if isinstance(path, TargetPixelFile):
				self._fromTPF(path)
			elif '.npy' in path:
				self.load(path)
			else:
				if type(path) == list:
					filenames = path
				elif '*' in path:
					filenames = glob.glob(path)[:limit]
				else:
					raise ValueError("{} can't be used to make a stamp.".format(path))
				self._fromSparseSubarrays(filenames, extension)

		self.tic_id = self.static['TIC_ID']
		self.cadence = self.static['INT_TIME']
		self.spm = self.static['SPM']
		self.cam = self.static['CAM']

		self.identifier= 'TIC{TIC_ID} (CAM{CAM} | {ROW_CENT}, {COL_CENT})'.format(**self.static)
		self.label = 'SPM{SPM} | {INT_TIME}s'.format(**self.static)

		# default to some particular view
		self.consider('counts')


	def _fromSparseSubarrays(self, filenames, extension=1):
		'''
		Create a stamp object, from one extension of a group
		of FITS files make by faus' sparse_subarray code.

		This can be slow, if you need to keep reading the entire
		subarray file every time you want to load each extension.

		For faster,
		'''

		# open the first one, to get some basic info
		hdus = fits.open(filenames[0])
		frame = hdus[0]
		star = hdus[extension]
		static = {} #star.header

		# make empty temporal arrays
		N = len(filenames)

		for key in ['SPM', 'CAM', 'INT_TIME']:
			static[key] = frame.header[key]
		for key in ['TIC_ID', 'COL_CENT', 'ROW_CENT']:
			static[key] = star.header[key]



		temporal = {}
		for key in ['QUAL_BIT', 'TIME', 'CADENCE']:
			temporal[key] = np.empty(N)
			temporal[key][0] = frame.header[key]
		int_time, spm, cam = static['INT_TIME'], static['SPM'], static['CAM']
		# nothing (yet) that acts as a spatial image
		spatial = {}

		# KLUDGE, to convert ccd1 and ccd2 to camaer coords
		#flip = static['COL_CENT'] < 4272/2
		#flip = static['ROW_CENT'] < 4156/2

		# make empty photon arrays
		#if flip:
		#	data = star.data.T
		#else:
		data = star.data
		photons = np.empty((N, data.shape[0], data.shape[1]))

		# populate each time point
		for i, f in enumerate(filenames):
			#print(i, f)

			# the 0th extension contains time-dependent info
			hdu = fits.open(f)
			h0, d0 = hdu[0].header, hdu[0].data

			# make sure we're still on the right one
			assert(h0['INT_TIME'] == int_time)
			assert(h0['SPM'] == spm)
			assert(h0['CAM'] == cam)
			for k in temporal.keys():
				temporal[k][i] = h0[k]

			# the 1st extension contains the data for this star
			h, d = hdu[extension].header, hdu[extension].data
			#if flip:
			#	photons[i,:,:] = d.T[::-1, ::-1]
			#else:
			photons[i,:,:] = d

		self.__init__(self, photons=photons, temporal=temporal, spatial=spatial, static=static)
		self.speak('populated {}'.format(self))
		#if flip:
		#	self.speak('applied a KLUDGE to CCD1 + CCD2 (COL_CENT<2136?)')

	def _fromTPF(self, tpf):
		'''
		Make a Stamp from a TPF file.
		'''

		# open the first one, to get some basic info
		static = {}
		for k in ['SPM', 'CAM', 'INT_TIME'] + ['TIC_ID', 'COL_CENT', 'ROW_CENT'] + ['QUAL_BIT', 'TIME', 'CADENCE']:
			try:
				static[k] = tpf.hdu[0].header[k]
			except KeyError:
				pass
		# make empty temporal arrays
		N = len(tpf.time)


		temporal = {}
		temporal['QUAL_BIT'] = tpf.quality
		temporal['TIME'] = tpf.astropy_time.gps
		temporal['CADENCE'] = tpf.cadenceno

		# nothing (yet) that acts as a spatial image
		spatial = {}

		# KLUDGE, to convert ccd1 and ccd2 to camaer coords
		#flip = static['COL_CENT'] < 4272/2
		#flip = static['ROW_CENT'] < 4156/2

		# make empty photon arrays
		#if flip:
		#	data = star.data.T
		#else:
		photons = tpf.flux

		self.__init__(self, photons=photons, temporal=temporal, spatial=spatial, static=static)
		self.speak('populated {}'.format(self))
		#if flip:
		#	self.speak('applied a KLUDGE to CCD1 + CCD2 (COL_CENT<2136?)')


	def calculate_differences(self):

		difference = copy.deepcopy(self)
		for k in self.temporal.keys():
			difference.temporal[k] = 0.5*(self.temporal[1:] + self.temporal[:-1])

		difference.photons = np.diff(self.photons, )

	def filename(self, directory='.'):
		'''The base filename for this stamp.'''

		#return os.path.join(directory, 'tic{TIC_ID}_{ROW_CENT}-{COL_CENT}_cam{CAM}_spm{SPM}_{INT_TIME}s.npy'.format(**self.static))
		return os.path.join(directory, 'cam{CAM}_spm{SPM}_tic{TIC_ID}_col{COL_CENT}_row{ROW_CENT}_{INT_TIME}s.npy'.format(**self.static))

	def load(self, filename):
		'''
		Load from a .npy file.
		'''

		# make sure we're dealing with a npy saved file
		assert('.npy' in filename)
		loaded = np.load(filename, encoding='latin1')[()]
		self.__init__(self, **loaded)
		self.speak('loaded from {}'.format(filename))

	def save(self, filename):
		'''
		Save to a .npy file.
		'''

		# make sure we're dealing with a npy saved file
		assert('.npy' in filename)

		# populate a dictionary to save
		tosave = {}
		for k in self._savable:
			tosave[k] = vars(self)[k]
		np.save(filename, tosave)
		self.speak('saved to {} at {}'.format(filename, Time.now().iso))
