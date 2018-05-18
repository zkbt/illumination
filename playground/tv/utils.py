from ..imports import *

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
