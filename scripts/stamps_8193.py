from playground.imports import *
from playground.tpf.stamps import *

orbit = 'orbit-8193'
sparse_pattern = '/pdo/ramp/zkbt/orbit-8193/cam*/*subarrays.fits'

orbit_directory = os.path.join('/pdo/ramp/zkbt', orbit)
mkdir(orbit_directory)
stamps_directory = os.path.join(orbit_directory, 'stamps')

split_times_to_stars(sparse_pattern, stamps_directory=stamps_directory, ntimes=None, nstars=None)
#process_sparse_into_stamps(sparse_pattern=sparse_pattern, stamps_directory=stamps_directory, ntimes=5, nstars=None)
