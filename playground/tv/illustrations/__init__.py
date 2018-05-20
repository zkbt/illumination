from .IllustrationBase import IllustrationBase, Row
from .Stamps import Stamps
from .FourCameras import FourCameras
from .SingleCamera import SingleCamera
from .SingleCameraWithZoom import SingleCameraWithZoom
from ..utils import create_test_fits
from ..animation import animate
from ...cosmics.stamps import create_test_stamp
import matplotlib.pyplot as plt

def test_SingleCamera():
    print("\nTesting a Single Camera illustration.")
    illustration = SingleCamera(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1)
    illustration.plot()
    filename = 'single-camera-animation.mp4'
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_FourCameras():
    print("\nTesting the Four Camera illustration.")
    data = {'cam{}'.format(i+1):[create_test_fits(rows=300, cols=300) for _ in range(10)] for i in range(4)}
    illustration = FourCameras(**data)
    illustration.plot()
    filename = 'four-camera-animation.mp4'
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_Stamps():
    print("\nTesting the Stamps illustration.")
    data = [create_test_stamp(cadence=120, n=25) for _ in range(4)]
    illustration = Stamps(data, sharecolorbar=False)
    illustration.plot()
    filename = 'stamps-animation.mp4'
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_SingleCameraWithZoom(position=(250, 50), size=(50,50)):
    print("\nTesting a Single Camera with a Zoom.")
    illustration = SingleCameraWithZoom(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1,
                    zoomposition=position, zoomsize=size)

    illustration.plot()
    filename = 'single-camera-zoom-animation.mp4'
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test():
    test_Stamps()
    test_SingleCamera()
    test_FourCameras()
    test_SingleCameraWithZoom()
