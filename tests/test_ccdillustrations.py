from playground.imports import *
from playground.tv.illustrations import *
from playground.cartoons import *
from playground.tv.zoom import *


directory = 'examples/'
mkdir(directory)


def test_CameraIllustration(N=10, **kw):
    print("\nTesting a Single Camera Illustration with CCDs.")

    separateccds = {'ccd{}'.format(i):[create_test_fits(rows=300, cols=300, circlescale=(i + 1)*40) for _ in range(N)] for i in [1,2,3,4]}
    illustration = CameraOfCCDsIllustration(**separateccds, ext_image=1, **kw)
    illustration.plot()
    filename = os.path.join(directory, 'single-camera-ccds-animation.mp4')
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_FourCameraIllustration(N=10, **kw):
    print("\nTesting a Four Camera Illustration with CCDs.")

    separatecameras = {'cam{}'.format(i):{'ccd{}'.format(i):[create_test_fits(rows=300, cols=300, circlescale=(i + 1)*40) for _ in range(N)] for i in [1,2,3,4]} for i in [1,2,3,4]}
    illustration = FourCameraIllustration(**separatecameras, ext_image=1, **kw)
    illustration.plot()
    filename = os.path.join(directory, 'four-camera-ccds-animation.mp4')
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

if __name__ == '__main__':
    one = test_CameraIllustration()
    four = test_FourCameraIllustration()
