from playground.imports import *
from playground.tv.illustrations import *
from playground.cartoons import *
from playground.tv.zoom import *
from playground.tv.tools import animate

directory = 'examples/'
mkdir(directory)


def test_CameraIllustration(N=10, **kw):
    print("\nTesting a Single Camera illustration.")
    illustration = CameraIllustration(
        data=[create_test_fits(rows=300, cols=300) for _ in range(N)], ext_image=1, **kw)
    illustration.plot()
    filename = os.path.join(directory, 'single-camera-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_FourCameraIllustration():
    print("\nTesting the Four Camera illustration.")
    data = {'cam{}'.format(i + 1): [create_test_fits(rows=300, cols=300)
                                    for _ in range(10)] for i in range(4)}
    illustration = FourCameraIllustration(**data)
    illustration.plot()
    filename = os.path.join(directory, 'four-camera-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_StampsIllustration():
    print("\nTesting the Stamps illustration.")
    data = [create_test_stamp(cadence=2, N=5, xsize=10, ysize=10)
            for _ in range(4)]
    illustration = StampsIllustration(data, sharecolorbar=False)
    illustration.plot()
    filename = os.path.join(directory, 'stamps-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_CameraIllustrationWithStamps():
    print("\nTesting a Single Camera with a Zoom.")
    illustration = SingleCameraWithZoomIllustration(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1,
                                                    zoomposition=position, zoomsize=size)

    illustration.plot()
    filename = os.path.join(directory, 'single-camera-zoom-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_CameraIllustrationWithStamps():
    print("\nTesting a Single Camera with some stamps.")
    illustration = CameraIllustration(
        data=[create_test_fits(rows=300, cols=300) for _ in range(10)])
    camera = illustration.frames['camera']
    xmax, ymax = camera.xmax, camera.ymax

    stamps = [create_test_stamp(col_cent=np.random.randint(1, xmax),
                                row_cent=np.random.randint(1, ymax))
              for i in range(10)]

    for s in stamps:
        f = add_stamp(illustration, s, zoom=100)

    illustration.plot()
    filename = os.path.join(
        directory, 'single-camera-localstamps-animation.mp4')
    #animate(illustration, filename)
    #print("Take a look at {} and see what you think!".format(filename))
    return illustration


if __name__ == '__main__':
    test_CameraIllustrationWithStamps()
    test_StampsIllustration()
    test_FourCameraIllustration()
    test_CameraIllustration()
    test_CameraIllustrationWithStamps()
