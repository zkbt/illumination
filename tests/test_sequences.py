from playground.tv.sequence import *
from playground.tv.utils import create_test_fits
from playground.tpf.stamps import create_test_stamp

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
