from playground.imports import *
from playground.tv import *
from playground.cartoons import *
from playground.tv.animation import animate

directory = 'examples/'
mkdir(directory)


def test_hybrid(howmany=5):
    tpfs = [create_test_tpf(N=10) for i in range(howmany)]
    lcs = [t.to_lightcurve() for t in tpfs]
    timeseries = [TimeseriesFrame(data=l) for l in lcs]
    imshows = [imshowFrame(data=t) for t in tpfs]
    i = HybridIllustration(imshows=imshows, timeseries=timeseries, sharecolorbar=False)
    i.plot()
    animate(i)

if __name__ == '__main__':
    a = test_hybrid()
