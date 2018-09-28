from .stamps import *

def establish_file_lists(sparse_pattern, stamps_directory='stamps', nstars=None):
	print('Searching for "{}"...'.format(sparse_pattern))

	# write a complete list of all the files
	total_filename = os.path.join(stamps_directory, 'everysinglefile.txt')
	if os.path.exists(total_filename):
		with open(total_filename, 'r') as total:
			total_files = total.read().splitlines()
		print('{} lists {} sparse subarray files total.'.format(total_filename, len(total_files)))
	else:
		total_files = glob.glob(sparse_pattern)
		print('Found {} sparse subarray files.'.format(len(total_files)))
		with open(total_filename, 'w') as total:
			total.writelines([name + '\n' for name in total_files])

	completed_filename = os.path.join(stamps_directory, 'completedfiles.txt')
	if os.path.exists(completed_filename):
		with open(completed_filename, 'r') as complete:
			completed_files = complete.read().splitlines()
	else:
		completed_files = []
	print("{} lists {} completed sparse subarray files.".format(completed_filename, len(completed_files)))

	remaining_files = list(total_files)
	for f in completed_files:
		remaining_files.remove(f)
	print("{} files remain to split!".format(len(remaining_files)))

	return remaining_files



def split_times_to_stars(sparse_pattern, stamps_directory='stamps', ntimes=None, nstars=None):
	'''
	Take a group of sparse subarray FITS files,
	and split them up into directories for stars,
	each filled with individual time points.

	These can then be reassembled into Stamps.

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
	sparse_files = establish_file_lists(sparse_pattern, stamps_directory)#glob.glob(sparse_pattern)[:ntimes]
	completed_filename = os.path.join(stamps_directory, 'completedfiles.txt')

	# loop over the files (times)
	for i, f in enumerate(sparse_files):

		print(f)
		# open this file (time)
		hdus = fits.open(f, memmap=False)[:nstars]

		# this is the whole frame
		frame = hdus[0]

		# loop over extensions (aka stars)
		for e in np.arange(0, len(hdus)):

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
			mkdir(directory)
			static_filename = os.path.join(directory, 'static.npy')
			#print('saved static information to {}'.format(static_filename))
			np.save(static_filename, static)

			# save the individual timestamp for this star
			timestamp_filename = os.path.join(directory, 'img-{:08}.npy'.format(i))
			np.save(timestamp_filename, (star.data, temporal))

		print('saved {} stars from file {}/{} at {} \r'.format(len(hdus), i+1, len(sparse_files), Time.now().iso))
		with open(completed_filename, 'a') as complete:
				completed_files = complete.write(f + '\n')
	return os.path.join(stamps_directory, 'cam*/cam*_spm*_tic*/')

def combine_times_to_stamps(directories_pattern, stamps_directory='stamps', ntimes=None, nstars=None):
	'''
	Convert a group of directories into Stamps.

	Parameters
	----------
	directories_pattern : str
		A search string for directories that contain a static.npy, and lots of img-*.npy files.

	ntimes : int
		How many times should be included? (defaults to all)

	nstars : int
		How many stars should be included? (defaults to all)

	'''
	stamps_directories = glob.glob(directories_pattern)[:nstars]

	# pull up all the stamp directories
	for star, d in enumerate(stamps_directories):
		print('   {} = {}'.format(star, d))
		print('')
		static_file = os.path.join(d, 'static.npy')
		static = np.load(static_file)[()]
		img_files = glob.glob(os.path.join(d, 'img-*.npy'))[:ntimes]

		N = len(img_files)
		for i, f in enumerate(img_files):
			#print(i, f)
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
