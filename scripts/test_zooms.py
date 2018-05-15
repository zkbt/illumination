from playground.cosmics.stamps import *
from playground.tv.frames import *
from playground.tv.illustrations import imshowCubes
from playground.tv.animation import animate

N = 4184
stamps = [create_test_stamp(cadence=2,
                            col_cent=np.random.randint(0, N),
                            row_cent=np.random.randint(0, N),
                            cam=np.random.randint(0, 4)
          for i in range(3)]

fos = FieldOfStamps(stamps)
fos.plot()
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
