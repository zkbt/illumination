from playground.tv.sequences import *
from playground.cartoons import *
from playground.imports import *

def test_Stamps():
	'''
	Run a test of Stamps_Sequence
	'''

	filename = 'temporarystamp.npy'
	stamp = create_test_stamp()
	stamp.save(filename)
	a = Stamp_Sequence(stamp)
	b = Stamp_Sequence(filename)
	return a, b

def test_FITS():
	'''
	Run a test of the FITS_Sequence.
	'''
	filename = 'temporarytest.fits'
	pattern = 'tempo*arytest.fits'
	hdulist = create_test_fits()
	hdulist.writeto(filename, overwrite=True)
	ext_image = 1

	a = FITS_Sequence(pattern, ext_image=ext_image)
	files = glob.glob(pattern)
	b = FITS_Sequence(files, ext_image=ext_image)
	c = FITS_Sequence(hdulist, ext_image=ext_image)
	d = FITS_Sequence(filename, ext_image=ext_image)
	e = FITS_Sequence([hdulist], ext_image=ext_image)

	return a,b,c,d,e


def test_TPF():
	'''
	Run a test of the TPF_Sequence.
	'''
	tpf = create_test_tpf()
	a = make_sequence(tpf)
	assert(isinstance(a, TPF_Sequence))
	return a



"""
def test_timeseries():
	'''
	Run a test of the Timeseries_Sequence.
	'''
	x = (np.linspace(0, 1)*u.day + Time.now()).jd
	y = np.random.normal(0, 1, len(x))
	a = make_sequence(x, y)
	assert(isinstance(a, Timeseries_Sequence))
	return a
"""

if __name__ == '__main__':
	test_timeseries()
	test_TPF()
	test_FITS()
	test_Stamps()
"""
def test_many_FITS(N=30):
	'''
	Run a test of the FITS_Sequence.
	'''

	for i in range(N):

		filename = 'temporarytest_{:04}.fits'.format(i)
		pattern = 'temporarytest_*.fits'
		hdulist = create_test_fits(rows=4, cols=6)
		hdulist.writeto(filename, overwrite=True)
		ext_image = 1
		print('saved {}'.format(filename))
		a = FITS_Sequence(pattern, ext_image=ext_image)

	return a
"""
