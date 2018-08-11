from playground.imports import *
from playground.tv.illustrations import *
from playground.cartoons import *
from playground.tv.zoom import *
from playground.tv.tools import animate

directory = 'examples/'
mkdir(directory)


def test_CameraIllustration(N=10, **kw):
    print("\nTesting a Single Camera illustration.")

    separateccds = {'ccd{}'.format(i):[create_test_fits(rows=300, cols=300) for _ in range(N)] for i in [1,2,3,4]}
    illustration = CameraOfCCDsIllustration(**separateccds, ext_image=1, **kw)
    illustration.plot()
    filename = os.path.join(directory, 'single-camera-ccds-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

if __name__ == '__main__':
    test_CameraIllustration()
