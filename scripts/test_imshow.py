from playground.cosmics.stamps import *
from playground.tv.frames import *
from playground.tv.illustrations import CubesIllustration
from playground.tv.animation import animate




plt.ion()
s = create_test_stamp(n=5)
f = imshowStampFrame(data=s)
f.plot()




stamps = []
s2 = create_test_stamp(n=180)
s120 = s2.stack(cadence=120)
stamps = [s2, s120]

#s120.photons = stamps['nocrm'].photons - stamps['onboardcrm'].photons*5/4
#    stamps['difference'].consider()

#stamps = [, create_test_stamp(cadence=120, n=3)]


#for i in range(4):
#    stamps.append(create_test_stamp())

ic = CubesIllustration(stamps)
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
