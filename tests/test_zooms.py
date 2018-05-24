from playground.tv.illustrations import *
from playground.tv.utils import create_test_fits
from playground.tv.animation import animate
from playground.cosmics.stamps import create_test_stamp
from playground.imports import *

directory = 'examples/'
mkdir(directory)
def test_SingleCameraWithZoom(position=(250, 50), size=(50,50)):
    print("\nTesting a Single Camera with a Zoom.")
    illustration = SingleCameraWithZoom(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1,
                    zoomposition=position, zoomsize=size)

    illustration.plot()
    filename = os.path.join(directory, 'single-camera-zoom-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_SingleCameraLocalZoom(N=3, testgeometry=False, zoom=10, size=(10,10)):
    '''
    Test the local zoom windows on a Single Camera.
    '''

    plt.ion()
    print("\nTesting a Single Camera illustration with local zooms.")
    nrows, ncols = 300, 300
    illustration = SingleCamera(data=[create_test_fits(rows=nrows, cols=ncols) for _ in range(10)], ext_image=1)

    if testgeometry:
        for row in [0,nrows]:
            for col in [0, ncols]:
                f = add_zoom(illustration, position=(col,row), zoom=zoom, size=size)
        f = add_zoom(illustration, position=(ncols/2,nrows/2), zoom=zoom, size=size)
        filename = 'single-camera-local-zoom-geometry-animation.mp4'
    else:
        for i in range(N):
            row, col = np.random.randint(0,nrows), np.random.randint(0,ncols)
            f = add_zoom(illustration, position=(col,row), zoom=zoom, size=size)
            f.titlefordisplay = ''
        filename = os.path.join(directory, 'single-camera-local-zoom-animation.mp4')
    illustration.plot()

    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_FourCameraLocalZoom(N=3, zoom=3, size=(50,50)):
    '''
    Test the local zooms on four cameras.
    '''

    plt.ion()
    print("\nTesting a FourCamera illustration with local zooms.")
    nrows, ncols = 300, 300

    data ={'cam{}'.format(i+1):[create_test_fits(rows=300, cols=300) for _ in range(10)] for i in range(4)}
    illustration = FourCameras(**data, ext_image=1)
    cameras='four'


    for i in range(N):
        row, col = np.random.randint(0,nrows), np.random.randint(0,ncols)
        f = add_zoom(illustration, camera='cam{}'.format(np.random.randint(1,5)),
                                  position=(col,row), zoom=zoom, size=size)
        f.titlefordisplay = ''
    filename = os.path.join(directory, '{}-camera-local-zoom-animation.mp4'.format(cameras))
    illustration.plot()
    #for x in plt.findobj():
    #    x.set_clip_on(True)
    #    print(x.get_clip_on(), x)

    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_SingleCameraWithStamps():
    print("\nTesting a Single Camera with some stamps.")
    illustration = SingleCamera(data=[])
    camera = illustration.frames['camera']
    xmax, ymax = camera.xmax, camera.ymax

    stamps = [create_test_stamp(col_cent=np.random.randint(1, xmax),
                                row_cent=np.random.randint(1, ymax))
                    for i in range(10)]

    for s in stamps:
        f = add_stamp(illustration, s, zoom=100)

    illustration.plot()
    filename = os.path.join(directory, 'single-camera-localstamps-animation.mp4')
    #animate(illustration, filename)
    #print("Take a look at {} and see what you think!".format(filename))
    return illustration
