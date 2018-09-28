'''
Make some cartoon datasets to play with.
'''

from .imports import *
from .postage.stamps import Stamp
from .postage.tpf import EarlyTessTargetPixelFile, EarlyTessLightCurve

def create_test_times(N=100, cadence=2):
    '''
    Create a fake array of times.
    '''
    return Time('2018-01-01 00:00:00.000', scale='tdb') + np.arange(N) * cadence * u.s


def create_test_array(N=100, xsize=5, ysize=5, nstars=None, single=False, seed=None):
    '''
    Create a fake stack of images of stars
    (with no cosmics injected, no jitter, Gaussian PDF).

    Parameters:
    -----------
    xsize : int
            The number of columns.
    ysize : int
            The number of rows.
    n : int
            The number of time points.
    single : bool
            Should this be just a single star, or should it be many?
    '''

    # seed the random number generator
    np.random.seed(seed)

    # create images of x, y, and an empty one to fill with stars
    x1d = np.arange(0, xsize)
    y1d = np.arange(0, ysize)
    x, y = np.meshgrid(x1d, y1d)
    stars = np.zeros_like(x)

    # create N random position for stars
    if single:
        nstars = 1
        sx = np.random.normal(xsize / 2.0, 1)
        sy = np.random.normal(ysize / 2.0, 1)
    else:
        if nstars is None:
            nstars = np.minimum(int(xsize * ysize / 4), 1000)
        sx = np.random.uniform(0, xsize, nstars)
        sy = np.random.uniform(0, ysize, nstars)

    # set some background level
    bg = 30

    # create a semi-reasonable magnitude distribution for stars
    if single:
        topmag = 5
    else:
        topmag = 10
    sf = 10000 * 10**(-0.4 * np.random.triangular(0, topmag, topmag, nstars))

    # define the cartoon PSF for the stars
    sigma = 1.0

    def gauss(x, y, x0, y0):
        return np.exp(-0.5 * ((x - x0)**2 + (y - y0)**2) / sigma**2)

    # create a cube with an image for each star, and sum them together into one image
    stars = (sf * gauss(x[:, :, np.newaxis],
                        y[:, :, np.newaxis], x0=sx, y0=sy)).sum(2)

    # create a model images
    model = (bg + stars)[np.newaxis, :, :] * np.ones(N).reshape((N, 1, 1))

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
    temporal['TIME'] = create_test_times(N=N, cadence=cadence)
    temporal['CADENCE'] = np.arange(N)
    temporal['QUAL_BIT'] = np.zeros(N).astype(np.int)

    return Stamp(spatial=spatial, photons=photons, temporal=temporal, static=static)


def create_test_lightcurve(N=100, cadence=2, **kwargs):
    '''
    Create a test lightkurve LightCurve object.
    '''
    time = create_test_times(N=N, cadence=cadence).jd
    flux = np.random.normal(1, 0.001, len(time))
    return EarlyTessLightCurve(time, flux)


def create_test_tpf(**kwargs):
    '''
    Create a test TargetPixelFile.

    Parameters
    ----------
    '''
    return EarlyTessTargetPixelFile.from_stamp(create_test_stamp(**kwargs))


def create_test_fits(rows=400, cols=600, circlescale=100, visualize=False, noise=0.2, seed=None):
    '''
    Create a test FITS image, mostly to help understand geometry.
    It has circles centered at 0 and a gradient toward positive x.
    '''

    # create x and y arrays
    x, y = np.meshgrid(np.arange(cols).astype(np.float),
                       np.arange(rows).astype(np.float))

    # put a dot near the origin, and a gradient in x
    z = 0.5 * np.max(x) * np.exp(-0.5 *
                                 np.sin((x**2 + y**2) / circlescale**2)**2) + x
    if noise is not None:
        np.random.seed(seed)
        sigma = noise * np.std(z)
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

def create_directory_of_fits(base='someplace', N=10, xsize=100, ysize=100, **kw):

    mkdir(base)
    for camera in [1,2,3,4]:
        directory = os.path.join(base, 'cam{}'.format(camera))
        mkdir(directory)
        for i in range(N):
            filename = os.path.join(directory, 'cam{}-{:04}.fits'.format(camera, i))
            if os.path.exists(filename):
                continue
            f = create_test_fits(rows=ysize, cols=xsize, circlescale=(i+1)*6, **kw)
            f.writeto(filename, overwrite=True)
            print(' saved cartoon image to {}'.format(filename))
