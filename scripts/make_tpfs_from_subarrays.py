from playground.imports import *
from playground.postage import *


files = glob.glob('/scratch2/zkbt/orbit-8196/subarrays/cam4/cam*.fits')

# this is the bright star Chelsea and Andrew were looking at
ext = 418

t = EarlyTessTargetPixelFile.from_sparse_subarrays(files[0:1000], ext=ext)
t.to_fits('/scratch2/zkbt/orbit-8196/{}-short-targ.fits'.format(t.tic_id))

t = EarlyTessTargetPixelFile.from_sparse_subarrays(files, ext=ext)
t.to_fits('/scratch2/zkbt/orbit-8196/{}}-targ.fits'.format(t.tic_id))
