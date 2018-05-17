from ..imports import *
from matplotlib.colors import SymLogNorm, LogNorm

def cmap_norm_ticks(a, whatpercentiles=[1,99], howmanysigmaarelinear=1.5, whatfractionislinear=0.15,  ):
	'''
	Return a probably pretty-OK colormap, a color normalization,
	and suggested tick marks for a colorbar, based on an input array.

	Parameters
	----------

	a : array
		The cmap and norm will be set on the basis of values in this array.
	'''

	# figure out a decent color scale
	vmin, vmax = np.percentile(a, whatpercentiles)
	if (a < 0).any():
		# go diverging, if this is a difference that crosses zero
		scale = np.maximum(np.abs(vmin), np.abs(vmax))
		vmin, vmax = -scale, scale
		span = np.log10(scale)
		sigma = mad(a)

		norm = SymLogNorm(howmanysigmaarelinear*sigma,
						  linscale=span*whatfractionislinear,
						  vmin=vmin, vmax=vmax)

		cmap = 'RdBu'
		ticks = [vmin, -howmanysigmaarelinear*sigma, 0, howmanysigmaarelinear*sigma, vmax]
	else:
		# go simple logarithmic, if this is all positive
		norm = LogNorm(vmin=vmin, vmax=vmax)
		cmap = 'Blues'
		ticks = [vmin, vmin*np.sqrt(vmax/vmin), vmax]

	return cmap, norm, ticks
