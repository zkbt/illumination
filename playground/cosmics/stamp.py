'''
This constructs a stamp, as a Cube, from a directory of
sparse_subaray files.
'''

from .imports import *
from .cubes import Cube



path = '/pdo/ramp/zkbt/orbit-8193/'
cam = 2
spm = 1

class Stamp(Cube):
	"""
	TESS postage stamp. Similar to a lightweight version of lightkurve.
	"""

	def __init__(self, path, extension=1, **kw):
		'''

		Parameters
		----------
		path : str, list of strings, list of HDULists
			A filename for a '.npy' file.
			A search path
		'''

		# figure out how to load the stamp
		if '.npy' in path:
			self.load(path)
		else:
			if type(path) == list:
				filenames = path
			elif '*' in path:
				filenames = glob.glob(path)
			else:
				raise ValueError("{} can't be used to make a stamp.".format(path))
			self._fromSparseSubarrays(filenames, extension)

		self.ticid = self.static['TIC_ID']
		self.camera = self.temporal['CAMERA'][0]
		self.cadence = self.temporal['INT_TIME'][0]
		self.spm = self.static['SPM'][0]



	def _fromSparseSubarrays(self, filenames, extension=1):
		'''
		Create a stamp object, from one extension of a group
		of FITS files make by faus' sparse_subarray code.
		'''

		# open the first one, to get some basic info
		hdus = fits.open(filenames[0])
		frame = hdus[0]
		star = hdus[extension]
		static = star.header

		# make empty temporal arrays
		N = len(filenames)
		temporal = {}
		for key in ['INT_TIME', 'QUAL_BIT', 'SPM', 'CAM', 'TIME', 'CADENCE']:
			temporal[key] = np.empty(N)
			temporal[key][0] = frame.header[key]

		# nothing (yet) that acts as a spatial image
		spatial = {}

		# make empty photon arrays
		data = star.data
		photons = np.empty((N, data.shape[0], data.shape[1]))

		# populate each time point
		for i, f in enumerate(filenames):

			# the 0th extension contains time-dependent info
			hdu = fits.open(f)
			h0, d0 = hdu[0].header, hdu[0].data

			# make sure we're still on the right onw
			assert(h0['INT_TIME'] == int_time)
			assert(h0['SPM'] == spm)
			assert(h0['CAM'] == cam)
			for k in keys:
				temporal[k][i] = h0[k]

			# the 1st extension contains the data for this star
			h, d = hdu[extension].header, hdu[extension].data
			photons[i,:,:] = d

		Cube.__init__(self, photons=photons, temporal=temporal, spatial=spatial, static=static)



	def load(self, filename):
		'''
		Load from a .npy file.
		'''

		# make sure we're dealing with a npy saved file
		assert('.npy' in file)
		loaded = np.load(filename)[()]
		Cube.__init__(self, **loaded)
		self.speak('loaded from {}'.format(filename))

	def save(self, filename):
		'''
		Save to a .npy file.
		'''

		# make sure we're dealing with a npy saved file
		assert('.npy' in file)

		# populate a dictionary to save
		tosave = {}
		for k in self.savable:
			tosave[k] = vars(self)[k]
		np.save(filename, tosave)
		self.speak('saved to {}'.format(filename))


s = Stamp('/pdo/ramp/zkbt/orbit-8193/cam1/cam1_spm1_*_sparse_subarrays.fits')

'''
# check out info for one of them
#hdu = fits.open(files[0])
#hdu.info()
#extensions = {(hdu[i].header['COL_CENT'], hdu[i].header['ROW_CENT']):i for i in np.arange(1, len(hdu))}
limit = 10

def make_cube(extension=1,
				cam=2, spm=1, path='/pdo/ramp/zkbt/orbit-8193/', limit=100):

	# find all files in this directory that are relevant
	search = os.path.join(path, 'cam{}'.format(cam), 'cam{}_spm{}*sparse_subarrays.fits'.format(cam, spm))
	files = glob.glob(search)

	# open the first one, to get some basic info
	first = fits.open(files[0])[extension]
	header = first.header
	data = first.data
	N = np.minimum(len(files), limit)
	array = np.empty((N, data.shape[0], data.shape[1]))
	oned = {}
	keys = ['INT_TIME', 'QUAL_BIT', 'TIME', 'CADENCE']
	for k in keys:
		oned[k] = np.empty(N)

	tic = header['TIC_ID']
	location = header['COL_CENT'], header['ROW_CENT']

	# populate each time point
	for i, f in enumerate(files[:limit]):
		print(f)

		# the 0th extension contains time-dependent info
		hdu = fits.open(f)
		h0, d0 = hdu[0].header, hdu[0].data
		assert(h0['SPM'] == spm)
		assert(h0['CAM'] == cam)
		for k in keys:
			oned[k][i] = h0[k]

		# the 1st extension contains the data for this star
		h, d = hdu[extension].header, hdu[extension].data
		array[i,:,:] = d

	return array

stamps = make_cube()


c = Cube(stamps, cadence=2)
c.movie()
c.imshow()



plt.savefig('/pdo/ramp/zkbt/example-stamp.pdf')

print('trying the big plot')
c.plot(normalization='median')
plt.savefig('/pdo/ramp/zkbt/example-stamp-grid-mediannormalized.pdf')

c.plot(normalization='none')
plt.savefig('/pdo/ramp/zkbt/example-stamp-grid-unnormalized.pdf')
'''
