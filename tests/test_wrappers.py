from playground.imports import *
from playground.cartoons import *
from playground.tv.tools import *
from playground.tv.tools import *

directory = 'examples/'
mkdir(directory)


def test_FITSwithZoom(zoomposition=(30, 70), zoomsize=(10, 10)):

    print("\nTesting a Single Camera with a Zoom.")

    for i in range(10):
        f = create_test_fits(rows=300, cols=300)
        f.writeto('test-{:04f}.fits'.format(i), overwrite=True)

    # create the illustration
    illustration = illustratefits(  'test-*.fits',
                                    ext_image=1,
                                    zoomposition=zoomposition,
                                    zoomsize=zoomsize)

    # plot and animate
    illustration.plot()
    filename = os.path.join(directory, 'illustatefits-zoom-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


if __name__ == '__main__':
    test_FITSwithZoom()
