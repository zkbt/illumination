from ..imports import *
from .illustrations import *
from .frames import ZoomFrame, LocalZoomFrame

def addZoom(illustration, position, size=(25,25), zoom=5, camera='camera'):
    '''
    Add a ZoomFrame to an illustration,
    at roughly its position.

    Parameters
    ----------
    illustration : an Illustration
        This is the overall illustration to which
        we want to be adding a local zoom.
    position : tuple
        (x,y) position of where the zoom should be centered
    size : tuple
        (nrows, ncols) shape of the region to zoom
    zoom : float
        By what factor do we magnify, relative to the original pixels
    camera : str
        Must exist as a key in the illustration.frames
    '''

    # to which frame do we add this?
    reference_frame = illustration.frames[camera]

    # define a key for this frame
    key = 'zoom-{}-({},{})'.format(camera, position[0], position[1])
    illustration.frames[key] = LocalZoomFrame(illustration=illustration,
                                    ax=None,
                                    source=reference_frame,
                                    position=position,
                                    size=size,
                                    zoom=zoom)

    return illustration.frames[key]

def test_Zooms(N=3, testgeometry=False, zoom=10, size=(10,10)):
    '''
    Test the local zoom windows on a Single Camera.
    '''

    plt.ion()
    print("\nTesting a Single Camera illustration.")
    nrows, ncols = 300, 300
    illustration = SingleCamera(data=[create_test_fits(rows=nrows, cols=ncols) for _ in range(10)], ext_image=1)

    if testgeometry:
        for row in [0,nrows]:
            for col in [0, ncols]:
                f = addZoom(illustration, position=(col,row), zoom=zoom, size=size)
        f = addZoom(illustration, position=(ncols/2,nrows/2), zoom=zoom, size=size)
        filename = 'single-camera-local-zoom-geometry-animation.mp4'
    else:
        for i in range(N):
            row, col = np.random.randint(0,nrows), np.random.randint(0,ncols)
            f = addZoom(illustration, position=(col,row), zoom=zoom, size=size)
            f.titlefordisplay = ''
        filename = 'single-camera-local-zoom-animation.mp4'
    illustration.plot()

    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


def test_FourCameraZooms(N=3, zoom=3, size=(50,50)):
    '''
    Test the local zooms on four cameras.
    '''

    plt.ion()
    print("\nTesting a SiFngle Camera illustration.")
    nrows, ncols = 300, 300

    data ={'cam{}'.format(i+1):[create_test_fits(rows=300, cols=300) for _ in range(10)] for i in range(4)}
    illustration = FourCameras(**data, ext_image=1)
    cameras='four'


    for i in range(N):
        row, col = np.random.randint(0,nrows), np.random.randint(0,ncols)
        f = addZoom(illustration, camera='cam{}'.format(np.random.randint(1,5)),
                                  position=(col,row), zoom=zoom, size=size)
        f.titlefordisplay = ''
    filename = '{}-camera-local-zoom-animation.mp4'.format(cameras)
    illustration.plot()
    for x in plt.findobj():
        x.set_clip_on(False)
        print(x.get_clip_on(), x)

    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration
