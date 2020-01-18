from illumination.sequences import *
from illumination.cartoons import *
from illumination.imports import *

directory = 'examples/'
mkdir(directory)

def test_Stamps():
    '''
    Run a test of Stamps_Sequence
    '''

    filename = os.path.join(directory, 'temporarystamp.npy')
    stamp = create_test_stamp()
    stamp.save(filename)
    a = Stamp_Sequence(stamp)
    b = Stamp_Sequence(filename)
    return a, b


def test_FITS():
    '''
    Run a test of the FITS_Sequence.
    '''
    filename = os.path.join(directory, 'temporarytest.fits')
    pattern = os.path.join(directory, 'tempo*arytest.fits')
    hdulist = create_test_fits()
    hdulist.writeto(filename, overwrite=True)
    ext_image = 1

    a = FITS_Sequence(pattern, ext_image=ext_image)
    files = glob.glob(pattern)
    b = FITS_Sequence(files, ext_image=ext_image)
    c = FITS_Sequence(hdulist, ext_image=ext_image)
    d = FITS_Sequence(filename, ext_image=ext_image)
    e = FITS_Sequence([hdulist], ext_image=ext_image)

    return a, b, c, d, e


def test_TPF():
    '''
    Run a test of the TPF_Sequence.
    '''
    tpf = create_test_tpf()
    a = make_image_sequence(tpf)
    assert(isinstance(a, TPF_Sequence))
    return a


def test_make():
    # a single image
    singleimage = create_test_array(N=1, xsize=20, ysize=10)[0]
    print(singleimage.shape, type(singleimage))
    make_image_sequence(singleimage)

    #multiple images
    manyimages = create_test_array(N=3, xsize=100, ysize=50)
    print(manyimages.shape, type(manyimages))
    make_image_sequence(manyimages)

    # stamp
    stamp = create_test_stamp()
    make_image_sequence(stamp)

    # fits
    fits = create_test_fits()
    make_image_sequence(fits)

    # multiple fits
    fits = [create_test_fits() for _ in range(10)]
    make_image_sequence(fits)


"""
def test_timeseries():
	'''
	Run a test of the Timeseries_Sequence.
	'''
	x = (np.linspace(0, 1)*u.day + Time.now()).jd
	y = np.random.normal(0, 1, len(x))
	a = make_image_sequence(x, y)
	assert(isinstance(a, Timeseries_Sequence))
	return a
"""

if __name__ == '__main__':
#    test_TPF()
#    test_FITS()
#    test_Stamps()
    test_make()
