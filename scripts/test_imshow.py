from playground.cosmics.stamps import *
from playground.tv.frames import *
from playground.tv.illustrations import imshowCubes
from playground.tv.animation import animate

#plt.ion()
s = create_test_stamp(n=5)
f = imshowStampFrame(data=s)
#f.plot()


stamps = []
for i in range(4):
    stamps.append(create_test_stamp())

ic = imshowCubes(stamps)
ic.plot()
animate(ic)
'''
    # plots
    plt.figure()
    for k in stamps.keys():
        t = stamps[k].time
        f = stamps[k].photons.sum(-1).sum(-1)
        plt.scatter(t, f/stamps[k].cadence, s=2, label=k)
    return stamps
'''
