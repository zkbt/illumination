from illumination.imports import *
from illumination.cartoons import *
from illumination.tools import *
from illumination.tools import *

filetemplate = 'cam{}-ccd{}.fits'
directory = 'examples/'
mkdir(directory)

def create_some_files():
    for cam in [1,2,3,4]:
        for ccd in [1,2,3,4]:
            filename = os.path.join(directory, filetemplate.format(cam, ccd))
            try:
                create_test_fits(100,100).writeto(filename)
            except OSError:
                print('{} already exists'.format(filename))

def test_organize():
    create_some_files()
    pattern = os.path.join(directory, 'cam*-ccd*-0000.fits')
    return organize_sequences(pattern)

def test_illustratefits():
    create_some_files()

    x = {'many':'*', 'one':1}
    for camera in ['one', 'many']:#, 'many']:
        for ccd in ['one']:#, 'many']:
            pattern = os.path.join(directory, filetemplate.format(x[camera], x[ccd]))
            i = illustratefits(pattern)
            i.plot()
            i.savefig(os.path.join(directory, 'camera={}-ccd={}.png'.format(camera, ccd)))


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
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration


if __name__ == '__main__':
    test_illustratefits()
    #test_FITSwithZoom()
