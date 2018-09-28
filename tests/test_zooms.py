from illumination.imports import *
from illumination.illustrations import *
from illumination.zoom import *
from illumination.cartoons import *


directory = 'examples/'
mkdir(directory)


def test_SingleCameraWithZoomIllustration(position=(250, 50), size=(50, 50)):
    print("\nTesting a Single Camera with a Zoom.")

    # create the illustration
    illustration = SingleCameraWithZoomIllustration(
        data=[create_test_fits(rows=300, cols=300) for _ in range(10)],
        ext_image=1,
        zoomposition=position, zoomsize=size)

    # plot and animate
    illustration.plot()
    filename = os.path.join(directory, 'single-camera-zoom-animation.mp4')
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_CameraIllustrationLocalZoom(N=3,
                                           testgeometry=False,
                                           zoom=10,
                                           size=(10, 10)):
    '''
    Test the local zoom windows on a Single Camera.
    '''

    print("\nTesting a Single Camera illustration with local zooms.")

    # create the illustration
    nrows, ncols = 300, 300
    illustration = CameraIllustration(
        data=[create_test_fits(rows=nrows, cols=ncols) for _ in range(10)],
        ext_image=1)

    # some options for where to add the stamps (corners, or random?)
    if testgeometry:
        for row in [0, nrows]:
            for col in [0, ncols]:
                f = add_zoom(illustration,
                             position=(col, row),
                             zoom=zoom,
                             size=size)
        f = add_zoom(illustration, position=(
            ncols / 2, nrows / 2), zoom=zoom, size=size)
        filename = 'single-camera-local-zoom-geometry-animation.mp4'
    else:
        for i in range(N):
            row, col = np.random.randint(0, nrows), np.random.randint(0, ncols)
            f = add_zoom(illustration,
                         position=(col, row),
                         zoom=zoom, size=size)
            f.titlefordisplay = ''
        filename = os.path.join(
            directory, 'single-camera-local-zoom-animation.mp4')

    # plot and animate
    illustration.plot()
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_FourCameraLocalZoom(N=3, zoom=3, size=(50, 50)):
    '''
    Test the local zooms on four cameras.
    '''

    # create the illustration
    print("\nTesting a FourCamera illustration with local zooms.")
    nrows, ncols = 300, 300
    data = {'cam{}'.format(i + 1): [create_test_fits(rows=300, cols=300)
                                    for _ in range(10)] for i in range(4)}
    illustration = FourCameraIllustration(**data, ext_image=1)

    # add some random zoom to it
    for i in range(N):
        row, col = np.random.randint(0, nrows), np.random.randint(0, ncols)
        f = add_zoom(illustration, camera='cam{}'.format(np.random.randint(1, 5)),
                     position=(col, row), zoom=zoom, size=size)
        f.titlefordisplay = ''

    # plot and animate
    filename = os.path.join(directory, 'four-camera-local-zoom-animation.mp4')
    illustration.plot()
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


"""
def test_CameraIllustrationWithStamps():
    print("\nTesting a Single Camera with some stamps.")

    # create illustration (of an empty camera)
    illustration = CameraIllustration()

    # make up some imaginary stamps
    camera = illustration.frames['camera']
    xmax, ymax = camera.xmax, camera.ymax
    stamps = [create_test_stamp(col_cent=np.random.randint(1, xmax),
                                row_cent=np.random.randint(1, ymax), N=10)
                    for i in range(10)]

    # add the stamps to the illustration
    for s in stamps:
        f = add_stamp(illustration, s, zoom=100)

    # plot and animate
    illustration.plot()
    filename = os.path.join(directory, 'single-camera-stamps-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_FourCameraWithStamps(N=3):
    print("\nTesting a Single Camera with some stamps.")

    # create empty four camera illustration
    illustration = FourCameraIllustration()

    # populate each camera with some stamps
    for c in [1,2,3,4]:
        camera = illustration.frames['cam{}'.format(c)]
        xmax, ymax = camera.xmax, camera.ymax
        stamps = [create_test_stamp(col_cent=np.random.randint(1, xmax),
                                    row_cent=np.random.randint(1, ymax), N=10)
                        for i in range(N)]

        for s in stamps:
            f = add_stamp(illustration, s, zoom=100, camera='cam{}'.format(c))

    # plot and animate
    illustration.plot()
    filename = os.path.join(directory, 'four-camera-stamps-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration
"""

if __name__ == '__main__':
    test_SingleCameraWithZoomIllustration()
    test_CameraIllustrationLocalZoom()
    test_FourCameraLocalZoom()
