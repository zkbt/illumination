from playground.process_sparse import *
#kaitain

orbit = 'orbit-8195'
sparse_pattern = '/opt/Data/TESS/Flight/orbits/orbit-8195/fits/*/*sparse_subarrays.fits'

orbit_directory = os.path.join('/opt/Data/TESS/Flight/zkbt', orbit)
mkdir(orbit_directory)
stamps_directory = os.path.join(orbit_directory, 'stamps')

split_times_to_stars(sparse_pattern, stamps_directory=stamps_directory, ntimes=None, nstars=None)
#process_sparse_into_stamps(sparse_pattern=sparse_pattern, stamps_directory=stamps_directory, ntimes=5, nstars=None)
