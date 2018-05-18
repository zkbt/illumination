from playground.imports import *
from playground.cosmics.stamps import *
from playground.tv.frames import *
from playground.tv.illustrations import FourCameras, SingleCamera
from playground.tv.animation import animate
from playground.tv.utils import create_test_fits

def test_SingleCamera():
    print("\nTesting a Single Camera illustration.")
    c = SingleCamera(data=[create_test_fits(rows=500, cols=500) for _ in range(10)] , ext_image=0)
    c.plot()
    animate(c, 'single-camera-animation.mp4')

def test_FourCamera():
    print("\nTesting the Four Camera illustration.")
    data = {'cam{}'.format(i+1):[create_test_fits(rows=500, cols=500) for _ in range(10)] for i in range(4)}
    fci = FourCameraIllustration(**data)
    fci.plot()
    animate(fci, filename='fourcamera-animation.mp4')


print("\nTesting with some real images.")
fci = FourCameraIllustration(
cam1='/Users/zkbt/Dropbox/TESS/may-visit/simulated/ffi/2s/ccd1/simulated*',
cam2='/Users/zkbt/Dropbox/TESS/may-visit/simulated/ffi/2s/ccd2/simulated*',
ext_image=0)
fci.plot()
animate(fci, filename='images-animation.mp4')



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
