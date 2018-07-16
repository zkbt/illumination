from playground.imports import *
from playground.tv import *
from playground.cartoons import *
from playground.tv.animation import animate

directory = 'examples/'
mkdir(directory)


def test_hybrid(howmany=3):
    tpfs = [create_test_tpf(N=50) for i in range(howmany)]
    lcs = [t.to_lightcurve() for t in tpfs]
    timeseries = [EmptyTimeseriesFrame(name='timeseries-{}'.format(i)) for i, l in enumerate(lcs)]
    imshows = [imshowFrame(data=t) for t in tpfs]
    i = HybridIllustration(imshows=imshows, timeseries=timeseries, sharecolorbar=False, figkw=dict(dpi=25))
    i.plot()
    for l, t in zip(lcs, timeseries):
        t.ax.plot(l.time - t.offset, l.flux)
    #animate(i)
    return i

if __name__ == '__main__':
    plt.ion()
    a = test_hybrid()
