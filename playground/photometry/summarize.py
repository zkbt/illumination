from .apertures import *


def photometer(tpf, **kw):

    # set the apertures
    define_apertures(tpf, **kw)
    plt.show()

    # subtract the background from the flux array
    subtract_background(tpf)

    #
    lc = tpf.to_lightcurve('pipeline')
    return lc
