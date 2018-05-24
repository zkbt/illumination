from playground.tv.illustrations import *
from playground.tv.utils import create_test_fits
from playground.tv.animation import animate
from playground.cosmics.stamps import create_test_stamp
from playground.imports import *

directory = 'examples/'
mkdir(directory)
def test_SingleCamera():
    print("\nTesting a Single Camera illustration.")
    illustration = SingleCamera(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1)
    illustration.plot()
    filename = os.path.join(directory, 'single-camera-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_FourCameras():
    print("\nTesting the Four Camera illustration.")
    data = {'cam{}'.format(i+1):[create_test_fits(rows=300, cols=300) for _ in range(10)] for i in range(4)}
    illustration = FourCameras(**data)
    illustration.plot()
    filename = os.path.join(directory, 'four-camera-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_Stamps():
    print("\nTesting the Stamps illustration.")
    data = [create_test_stamp(cadence=120, n=25, xsize=10, ysize=10) for _ in range(4)]
    illustration = Stamps(data, sharecolorbar=False)
    illustration.plot()
    filename = os.path.join(directory, 'stamps-animation.mp4')
    animate(illustration, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

def test_SingleCameraWithZoom(position=(250, 50), size=(50,50)):
    print("\nTesting a Single Camera with a Zoom.")
    illustration = SingleCameraWithZoom(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1,
                    zoomposition=position, zoomsize=size)

    illustration.plot()
    filename = os.path.join(directory, 'single-camera-zoom-animation.mp4')
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
