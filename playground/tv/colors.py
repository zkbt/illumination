from ..imports import *
from matplotlib.colors import SymLogNorm, LogNorm


def cmap_norm_ticks(a, whatpercentiles=[1, 99], howmanysigmaarelinear=1.5, whatfractionislinear=0.15, vmax=None):
    '''
    Return a probably pretty-OK colormap, a color normalization,
    and suggested tick marks for a colorbar, based on an input array.

    Parameters
    ----------

    a : array
            The cmap and norm will be set on the basis of values in this array.
    '''

    # figure out a decent color scale
    if (a <= 0).any():
        # go diverging, if this is a difference that crosses zero
        if vmax is not None:
            vmin = -vmax
        else:
            scale = np.maximum(np.abs(vmin), np.abs(vmax))
            vmin, vmax = -scale, scale
        span = np.log10(vmax)
        sigma = mad(a)

        norm = SymLogNorm(howmanysigmaarelinear * sigma,
                          linscale=span * whatfractionislinear,
                          vmin=vmin, vmax=vmax)

        cmap = 'RdBu'
        ticks = [vmin, -howmanysigmaarelinear * sigma,
                 0, howmanysigmaarelinear * sigma, vmax]
    else:
        if vmax is not None:
            vmin = np.percentile(a, whatpercentiles[0])
        else:
            vmin, vmax = np.percentile(a, whatpercentiles)

        # go simple logarithmic, if this is all positive
        norm = LogNorm(vmin=vmin, vmax=vmax)
        cmap = 'Blues'
        ticks = [vmin, vmin * np.sqrt(vmax / vmin), vmax]

    return cmap, norm, ticks
