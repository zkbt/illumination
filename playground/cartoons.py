from .imports import *
from .postage.stamps import Stamp
from .postage.tpf import EarlyTessTargetPixelFile

def create_test_array(xsize=5, ysize=5, n=100):
	'''
	Create a fake stack of images of stars
	(with no cosmics injected, no jitter, Gaussian PDF).
	'''

	# create images of x, y, and an empty one to fill with stars
	x1d = np.arange(0, xsize)
	y1d = np.arange(0, ysize)
	x, y = np.meshgrid(x1d, y1d)
	stars = np.zeros_like(x)

	# create N random position for stars
	N = int(xsize*ysize/4)
	sx = np.random.uniform(0, xsize, N)
	sy = np.random.uniform(0, ysize, N)

	# set some background level
	bg = 30

	# create a semi-reasonable magnitude distribution for stars
	sf = 10000*10**(-0.4*np.random.triangular(0, 10, 10, N))

	# define the cartoon PSF for the stars
	sigma = 1.0
	def gauss(x, y, x0, y0):
		return np.exp(-0.5*((x-x0)**2 + (y-y0)**2)/sigma**2)

	# create a cube with an image for each star, and sum them together into one image
	stars = (sf*gauss(x[:,:,np.newaxis], y[:,:,np.newaxis], x0=sx, y0=sy)).sum(2)

	# create a model images
	model = (bg + stars)[np.newaxis,:,:]*np.ones(n).reshape((n, 1, 1))

	# add some noise to it
	image = np.random.normal(model, np.sqrt(model))

	return image


def create_test_stamp(col_cent=3900, row_cent=913, cadence=2, cam=1, spm=1, tic_id=1234567890, **kw):

	static = {'CAM': cam,
	 'COL_CENT': col_cent,
	 'INT_TIME': cadence,
	 'ROW_CENT': row_cent,
	 'SPM': spm,
	 'TIC_ID': tic_id}

	spatial = {}

	photons = create_test_array(**kw)
	N = photons.shape[0]
	temporal = {}
	for k in ['TIME', 'CADENCE']:
		temporal[k] = Time('2018-01-01 00:00:00.000').gps + np.arange(N)*cadence
	temporal['QUAL_BIT'] = np.zeros(N).astype(np.int)

	return Stamp(spatial=spatial, photons=photons, temporal=temporal, static=static)


def create_test_tpf(**kwargs):
	
	return EarlyTessTargetPixelFile.from_stamp(create_test_stamp(**kwargs))

def create_test_fits(rows=400, cols=600, circlescale=100, visualize=False, noise=0.2, seed=None):
	'''
	Create a test FITS image, mostly to help understand geometry.
	It has circles centered at 0 and a gradient toward positive x.
	'''

	# create x and y arrays
	x, y = np.meshgrid(np.arange(cols).astype(np.float), np.arange(rows).astype(np.float))

	# put a dot near the origin, and a gradient in x
	z = 0.5*np.max(x)*np.exp(-0.5*np.sin((x**2 + y**2)/circlescale**2)**2) + x
	if noise is not None:
		np.random.seed(seed)
		sigma = noise*np.std(z)
		z = np.random.normal(z, sigma)

	hdulist = fits.HDUList([fits.PrimaryHDU(),
							fits.ImageHDU(z, name='image'),
							fits.ImageHDU(x, name='x'),
							fits.ImageHDU(y, name='y')])
	#hdulist[0].header['TIME'] = 42.0

	if visualize:

		plt.subplot(131)
		plt.imshow(x, origin='lower')
		plt.title('x')
		plt.subplot(132)
		plt.imshow(y, origin='lower')
		plt.title('y')
		plt.subplot(133)
		plt.title('z')
		plt.imshow(z, origin='lower')

	return hdulist
