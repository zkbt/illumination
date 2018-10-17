'''
Tools for setting up colors for display.
'''

from .imports import *
from matplotlib.colors import SymLogNorm, LogNorm

def cmap_norm_ticks(a, whatpercentiles=[1, 99], howmanysigmaarelinear=1.5, whatfractionislinear=0.15, vmax=None, vmin=None, cmap=None):
    '''
    Return a probably pretty-OK colormap, a color normalization,
    and suggested tick marks for a colorbar, based on an input array.

    Parameters
    ----------

    a : array
            The cmap and norm will be set on the basis of values in this array.
    '''

    if vmin is None:
        gonegative = (a <= 0).any()
    else:
        gonegative = vmin < 0

    # figure out a decent color scale
    if gonegative:
        # go diverging, if this is a difference that crosses zero
        if vmax is not None:
            vmin = -vmax
        else:
            vmin, vmax = np.nanpercentile(a, whatpercentiles)
            scale = np.maximum(np.abs(vmin), np.abs(vmax))
            vmin, vmax = -scale, scale
        span = np.log10(vmax)
        sigma = mad(a)

        norm = SymLogNorm(howmanysigmaarelinear * sigma,
                          linscale=span * whatfractionislinear,
                          vmin=vmin, vmax=vmax)
        if cmap is None:
            cmap = 'RdBu'
        ticks = [vmin, -howmanysigmaarelinear * sigma,
                 0, howmanysigmaarelinear * sigma, vmax]
    else:
        if vmax is None:
            vmax = np.nanpercentile(a, whatpercentiles[1])
        if vmin is None:
            vmin = np.nanpercentile(a, whatpercentiles[0])

        # go simple logarithmic, if this is all positive
        norm = LogNorm(vmin=vmin, vmax=vmax)
        if cmap is None:
            cmap = 'Blues'
        ticks = [vmin, vmin * np.sqrt(vmax / vmin), vmax]

    return cmap, norm, ticks
