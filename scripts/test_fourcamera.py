from playground.imports import *
from playground.cosmics.stamps import *
from playground.tv.frames import *
from playground.tv.illustrations import FourCameraIllustration, ZoomsIllustration
from playground.tv.animation import animate
from playground.tv.utils import create_test_fits

data = {'cam{}'.format(i+1):create_test_fits(rows=500, cols=500) for i in range(4)}
fci = FourCameraIllustration(**data)
fci.plot()
#fos.plot()
#animate(ic)
'''
    # plots
    plt.figure()
    for k in stamps.keys():
        t = stamps[k].time
        f = stamps[k].photons.sum(-1).sum(-1)
        plt.scatter(t, f/stamps[k].cadence, s=2, label=k)
    return stamps
'''
