from playground.imports import *
from playground.tv import *
from playground.cartoons import *
from playground.tv.animation import animate

directory = 'examples/'
mkdir(directory)


def test_hybrid(howmany=3):
    tpfs = [create_test_tpf(N=10, xsize=8, ysize=8) for i in range(howmany)]
    lcs = [t.to_lightcurve() for t in tpfs]
    timeseries = [EmptyTimeseriesFrame(
        name='timeseries-{}'.format(i)) for i, l in enumerate(lcs)]
    imshows = [imshowFrame(data=t) for t in tpfs]
    names = ['zip', 'zap', 'zoop']
    for x in range(howmany):
        timeseries[x].titlefordisplay = names[x]
        imshows[x].titlefordisplay = 'TIC{}\n{}'.format(
            tpfs[x].tic_id, names[x])

    i = HybridIllustration(imshows=imshows, timeseries=timeseries,
                           sharecolorbar=False, figkw=dict(dpi=50))
    i.plot()
    for l, t in zip(lcs, timeseries):
        t.ax.plot(l.time - t.offset, l.flux)
    animate(i)
    return i


if __name__ == '__main__':
    plt.ion()
    a = test_hybrid()
