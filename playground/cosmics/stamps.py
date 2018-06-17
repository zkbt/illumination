'''
This constructs a stamp, as a Cube, from a directory of
sparse_subaray files.
'''

from ..imports import *
from .cubes import Cube, create_test_array
from astropy.time import Time


path = '/pdo/ramp/zkbt/orbit-8193/'
cam = 2
spm = 1

class Stamp(Cube):
	"""
	TESS postage stamp. Similar to a lightweight version of lightkurve.
	"""

	def __init__(self, path=None, extension=1, limit=None,
				 photons=None, spatial={}, static={}, temporal={}, **kw):
		'''

		Parameters
		----------
		path : str, list of strings, list of HDULists
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
			if '.npy' in path:
				self.load(path)
			else:
				if type(path) == list:
					filenames = path
				elif '*' in path:
					filenames = glob.glob(path)
					if limit < len(filenames):
						filenames = filenames[:limit]
				else:
					raise ValueError("{} can't be used to make a stamp.".format(path))
				self._fromSparseSubarrays(filenames, extension)

		self.ticid = self.static['TIC_ID']
		self.cadence = self.static['INT_TIME']
		self.spm = self.static['SPM']
		self.cam = self.static['CAM']

		self.identifier= 'TIC{TIC_ID}\n(CAM{CAM} | {ROW_CENT}, {COL_CENT})'.format(**self.static)
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
		loaded = np.load(filename)[()]
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


def split_times_to_stars(pattern, stamps_directory='stamps', ntimes=None, nstars=None):
	'''
	Take a group of sparse subarray FITS files,
	and split them up into directories for stars,
	each filled with individual time points.

	These can then be reassembled into Stamps.

	Parameters
	----------

	pattern : str
		A search string pattern for sparse subarray files.

	stamps_directory : str
		Directory into which all the stamps will be stored (organized by camera).

	ntimes : int
		How many times should be included? (defaults to all)

	nstars : int
		How many stars should be included? (defaults to all)

	Returns
	-------

	directories_pattern : str
		A search string pattern that will capture all the directories just created.
	'''

	# make sure the stamps directory exists
	mkdir(stamps_directory)
	for cam in [1,2,3,4]:
		mkdir(os.path.join(stamps_directory, 'cam{}'.format(cam)))

	# make a list of sparse subarray files
	sparse_files = glob.glob(pattern)[:ntimes]

	# loop over the files (times)
	for i, f in enumerate(sparse_files):

		# open this file (time)
		hdus = fits.open(f, memmap=False)[:nstars]

		# this is the whole frame
		frame = hdus[0]

		# loop over extensions (aka stars)
		for e in np.arange(1, len(hdus)):

			# this is the one specific star
			star = hdus[e]

			# create the static dictionary for this star
			static = {}

			# store the items that are static to this star
			for key in ['SPM', 'CAM', 'INT_TIME']:
				static[key] = frame.header[key]
			for key in ['TIC_ID', 'COL_CENT', 'ROW_CENT']:
				static[key] = star.header[key]

			temporal = {}
			for key in ['QUAL_BIT', 'TIME', 'CADENCE']:
				temporal[key] = frame.header[key]

			# where should the timestamps be stored
			directory = os.path.join(stamps_directory, 'cam{CAM}/cam{CAM}_spm{SPM}_tic{TIC_ID}'.format(**static))

			# save the static information once
			if i == 0:
				mkdir(directory)
				static_filename = os.path.join(directory, 'static.npy')
				#print('saved static information to {}'.format(static_filename))
				np.save(static_filename, static)

			# save the individual timestamp for this star
			timestamp_filename = os.path.join(directory, 'img-{:08}.npy'.format(i))
			np.save(timestamp_filename, (star.data, temporal))

		print('saved {} stars from file {}/{} at {} \r'.format(len(hdus), i+1, len(sparse_files), Time.now().iso))
	return os.path.join(stamps_directory, 'cam*/cam*_spm*_tic*/')

def combine_times_to_stamps(directories_pattern, stamps_directory='stamps', ntimes=None, nstars=None):
	'''
	Convert a group of directories into Stamps.

	Parameters
	----------
	directories_pattern : str
		A search string for directories that contain a static.npy, and img-*.npy files.

	ntimes : int
		How many times should be included? (defaults to all)

	nstars : int
		How many stars should be included? (defaults to all)

	'''
	stamps_directories = glob.glob(directories_pattern)[:nstars]

	# pull up all the stamp directories
	for star, d in enumerate(stamps_directories):
		static_file = os.path.join(d, 'static.npy')
		static = np.load(static_file)[()]
		img_files = glob.glob(os.path.join(d, 'img-*.npy'))[:ntimes]

		N = len(img_files)
		for i, f in enumerate(img_files):
			image, temp = np.load(f)
			if i == 0:
				temporal = dict(**temp)
				for k in temporal.keys():
					temporal[k] = np.empty(N).astype(type(temporal[k]))
				photons = np.zeros((N, image.shape[0], image.shape[1]))
			for k in temporal.keys():
				temporal[k][i] = temp[k]
			photons[i,:,:] = image
		print('{}/{}'.format(star, len(stamps_directories)))
		s = Stamp(photons=photons, static=static, temporal=temporal)
		directory = os.path.join(stamps_directory, 'cam{CAM}'.format(**static))
		s.save(s.filename(directory))

		print('removing all files in {}'.format(d))
		shutil.rmtree(d)

def process_sparse_into_stamps(sparse_pattern, stamps_directory, **kw):
	'''
	Construct a bunch of Stamps from a bunch of sparse subarray files.

	Parameters
	----------

	sparse_pattern : str
		A search string pattern for sparse subarray files.

	stamps_directory : str
		Directory into which all the stamps will be stored (organized by camera).

	ntimes : int
		How many times should be included? (defaults to all)

	nstars : int
		How many stars should be included? (defaults to all)
	'''
	directories_pattern = split_times_to_stars(sparse_pattern, stamps_directory=stamps_directory, **kw)
	combine_times_to_stamps(directories_pattern, stamps_directory=stamps_directory, **kw)

"""
def populate(sparse_subarray_directory='/pdo/ramp/zkbt/orbit-8193/', stamps_directory='stamps/', cam=1, spm=1, extensions=3, limit=None):
	'''
	Populate a bunch of stamps, from a directory of sparse subarrays.
	'''

	subarray_files = glob.glob(os.path.join(sparse_subarray_directory, 'cam{cam}/cam{cam}_spm{spm}*.fits'.format(**locals())))
	#hdus = [fits.open(f) for f in subarray_files[:limit]]

	mkdir(stamps_directory)
	subdirectory = os.path.join(stamps_directory, 'spm{}'.format(spm))
	mkdir(subdirectory)

	stamps = []
	for i in range(extensions):
		extension = i + 1
		try:
			print("populating (EXT={}, CAM={}, SPM={})".format(extension, cam, spm))
			s = Stamp(subarray_files[:limit], extension=extension)
			s.save(s.filename(subdirectory))
			stamps.append(s)
		except IndexError:
			print("stopped before extension [{}]".format(extension))
			break
	return stamps

def organize(**kw):
	for cam in [1,2,3,4]:
		for spm in [1, 2, 3]:
			populate(spm=spm, cam=cam, **kw)
"""

def create_test_stamp(col_cent=3900, row_cent=913, cadence=2, cam=1, spm=1, tic_id=1234567890, **kw):

	static = {'CAM': cam,
	 'COL_CENT': col_cent,
	 'INT_TIME': cadence,
	 'ROW_CENT': row_cent,
	 'SPM': spm,
	 'TIC_ID': tic_id}

	spatial = {}

	photons = create_test_array(**kw)
	N = photons.shape[0]
	temporal = {}
	for k in ['TIME', 'CADENCE']:
		temporal[k] = np.arange(N)*cadence
	temporal['QUAL_BIT'] = np.zeros(N).astype(np.int)

	return Stamp(spatial=spatial, photons=photons, temporal=temporal, static=static)


def example():
	try:
		s = Stamp('/pdo/ramp/zkbt/orbit-8193/cam1/cam1_spm1_*_sparse_subarrays.fits')
	except IndexError:
		s = create_test_stamp()
	return s
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
