from playground.imports import *
from playground.postage import *


files = glob.glob('/scratch2/zkbt/orbit-8196/subarrays/cam4/cam*.fits')
ext = 418
t = EarlyTessTargetPixelFile.from_sparse_subarrays(files[0:10000], ext=1)
t.to_fits('/scratch2/zkbt/orbit-8196/381949122-short-targ.fits')

t = EarlyTessTargetPixelFile.from_sparse_subarrays(files, ext=1)
t.to_fits('/scratch2/zkbt/orbit-8196/381949122-targ.fits')
