from illumination.imports import *
from illumination.illustrations import *
from illumination.cartoons import *
from illumination.zoom import *


directory = 'examples/'
mkdir(directory)


def test_subtraction(N=10, **kw):
    print("\nTesting a Single Camera illustration.")

    sequence = make_image_sequence([create_test_fits(rows=300, cols=300) for _ in range(N)], ext_image=1)
    normal = imshowFrame(data=sequence, title='normal')
    subtracted = imshowFrame(data=sequence, title='median-subtracted')
    subtracted.processingsteps = ['subtractmedian']

    illustration = GenericIllustration(imshows=[normal, subtracted], **kw)

    illustration.plot()
    filename = os.path.join(directory, 'median-subtraction-animation.mp4')
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))
    return illustration

if __name__ == '__main__':
    test_subtraction()
