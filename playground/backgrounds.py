import warnings
import numpy as np
import matplotlib.pyplot as plt
from astropy.modeling import models, fitting
from matplotlib.patches import Ellipse
from craftroom.cmaps import one2another
okcmap = one2another('red', 'red', alphabottom=0.3, alphatop=0)

def create_test_image(gap=3, N=25):
    '''
    Create one random stitched camera, with a Gaussian-ish background to it.
    '''

    # generate a random model
    p_generate = (models.Const2D(amplitude=10**np.random.uniform(0, 1)) +
               models.Gaussian2D(amplitude=10**np.random.uniform(.5, 2),
                                   x_mean=np.random.uniform(-N, N),
                                   y_mean=np.random.uniform(-N, N),
                                   x_stddev=np.random.uniform(2, N),
                                   y_stddev=np.random.uniform(2, N),
                                   theta=np.random.uniform(0, 2*np.pi)))

    # create fake x and y arrays
    x, y = np.meshgrid(np.arange(-N-gap, N+gap+1), np.arange(-N-gap, N+gap+1))

    # create the model
    perfect = p_generate(x, y)
    z = np.random.normal(perfect, 1)

    # find the gaps, replace them with zeros, and mark them as bad
    bad = (np.abs(x) < gap) | (np.abs(y) < gap)
    z[bad] = 0
    ok = bad == False

    return x, y, z, ok, p_generate

def showimage(x, y, z, ok, **kw):
    '''
    Use imshow to show all four CCDs.
    '''
    imshowkw = dict(origin='lower',
                    extent=[np.min(x), np.max(x), np.min(y), np.max(y)],
                    interpolation='nearest', **kw)

    # show the image
    plt.imshow( z, **imshowkw)

    # mask out the neglected pixels
    imshowkw['cmap'] = okcmap
    imshowkw['vmin'] = 0
    imshowkw['vmax'] = 1

    plt.imshow(ok, **imshowkw)
    plt.axis('scaled')

def bin_image(image, binning=100, visualize=False):
    '''
    Bin an image down by a given factor,
    by taken the means of squares of pixels.

    Parameters
    ----------
    image : a

    '''
    rows = image.shape[0]//binning
    binnedoverrow = image[:rows*binning, :].reshape(rows, binning, image.shape[1]).mean(1)
    cols = image.shape[1]//binning
    binned = binnedoverrow[:,:cols*binning].reshape(binnedoverrow.shape[0], cols, binning).mean(2)

    if visualize:
        plt.imshow(binned)
        plt.colorbar()

    return binned

def guess_2d_gaussian(x, y, z, ok=None):
    '''
    Make a guess to initialize the baseline + 2D Gaussian model,
    based on medians and weighted moments of the image.
    '''

    if ok == None:
        ok = np.ones_like(z).astype(np.bool)

    # estimate a baseline flux, from the median of the good pixels
    baseline_guess = np.median(z[ok])

    # do a *veyr* coarse subtraction, to focus on just the blob
    crudelysubtracted = np.maximum((z-baseline_guess), 0)
    amplitude_guess = np.sum(crudelysubtracted)


    def moment(q):
        '''
        Take the weighted moment of a quantity.
        '''
        return np.sum(q[ok]*crudelysubtracted[ok])/np.sum(crudelysubtracted[ok])

    # calculate flux-weighted centroids of the blob
    x_guess = moment(x)
    y_guess = moment(y)

    # calculate flux-weighted widths of the blob
    x_width_guess = np.sqrt(moment((x - x_guess)**2))
    y_width_guess = np.sqrt(moment((y - y_guess)**2))



    # create an initial model, with the initial guesses
    initial = (  models.Const2D(amplitude=baseline_guess) +
                models.Gaussian2D(amplitude=amplitude_guess,
                               x_mean=x_guess, y_mean=y_guess,
                               x_stddev=x_width_guess, y_stddev=y_width_guess,
                               theta=0.0))

    return initial


    # fit it (binning by 100)
    p = bg.fit_2d_gaussian(x, y, crudelysubtracted, imagebinning=25, baseline=0, amplitude=500,
                                                           x_mean=x_guess, y_mean=y_guess,
                                                           x_stddev=500, y_stddev=500, theta=np.pi/4)
    #plot_fit(xsmall, ysmall, zsmall, truth)
    bg.plot_fit(x, y, image, p)
    plt.scatter(x_guess, y_guess, color='green')

    print(f)
    print(x_guess, y_guess, baseline_guess)
    #plt.colorbar()
    #plt.suptitle(f + '\n\n')
    plt.show()

def fit_model(x, y, z, ok=None, model=None, imagebinning=1, **kw):
    '''
    Fit the scattered light in a list of images (with x, y, z) for each.

    Parameters
    ----------
    x, y, z : 2D arrays
        The x and y values of each pixel (kind of boring images), and the z flux of the image.
    ok : 2D array
        Mask set to 1 where data are OK, 0 where they should be ignored.
    model : an astropy Model
        The initialized model to fit.
    imagebinning : int
        By how many pixels should the images be binned?
        This substantially speeds up fitting.
    p_init : an
        Initial guesses for the parameters of Gaussian2D.

    '''


    # construct the fitter (using LM)
    fit_p = fitting.LevMarLSQFitter()

    # run the fit (skipping some warnings)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        # if desired, bin the data
        if imagebinning == 1:
            bx, by, bz, bok = x, y, z, ok
        else:
            bx = bin_image(x, binning=imagebinning)
            by = bin_image(y, binning=imagebinning)
            bz = bin_image(z, binning=imagebinning)
            # (exclude bins that are only partially OK)
            bok = bin_image(ok, binning=imagebinning) == 1

        # run the fit, starting with initial model and comparing to the data
        p = fit_p(model, bx[bok], by[bok], bz[bok])

    return p

def plot_2d_gaussian(p, color='darkorchid', **kw):
    '''
    Using an astropy model Gaussian2D, plot it on an image.
    **kw go into Ellipse definition
    '''

    # plot the ellipse on each image
    baseline, gaussian = p
    e = dict(zip(gaussian.param_names, gaussian.parameters))
    howmanysigma = 2
    ellipse = Ellipse(xy=(e['x_mean'], e['y_mean']),
                      width=howmanysigma*e['x_stddev'],
                      height=howmanysigma*e['y_stddev'],
                      angle=e['theta']*180/np.pi,
                      linewidth=3, facecolor='none',
                      edgecolor=color, alpha=0.5, **kw)
    plt.gca().add_artist(ellipse)


def plot_fit(x, y, z, ok, models=None, colors=None, cmap='gray', **kw):
    '''
    Plot images along with their 2D Gaussian model.

    x, y, z : the two coordinate images and the flux image
    p : the model 2D Gaussian to plot, using an ellipse as summary

    **kw goes into showimage
    '''

    # set the scale for the image to plot
    vmin, vmax = np.percentile(z, [0, 100])

    # plot the data with the best-fit model
    fi, ax = plt.subplots(1, 3, figsize=(8, 2.5), sharex=True, sharey=True)


    fitted = models[0]
    plt.sca(ax[0])
    showimage(x, y, z, ok, vmin=vmin, vmax=vmax, cmap=cmap, **kw)

    for m, c in zip(models, colors):
        plot_2d_gaussian(m, color=c)
    plt.axis('off')
    plt.xlabel("Data")

    plt.sca(ax[1])
    showimage(x, y, fitted(x,y), ok, vmin=vmin, vmax=vmax, cmap=cmap, **kw)
    for m, c in zip(models, colors):
        plot_2d_gaussian(m, color=c)
    plt.axis('off')
    plt.xlabel("Model")

    plt.sca(ax[2])
    showimage(x, y, z-fitted(x,y), ok, vmin=vmin, vmax=vmax, cmap=cmap, **kw)
    for m, c in zip(models, colors):
        plot_2d_gaussian(m, color=c)
    plt.axis('off')
    plt.xlabel("Residual")

def load_camera(filename):
    '''
    Load a stitched full camera image.

    Parameters
    ----------
    filename : string
        The path to a FITS file containing faus' background images.
        (for example, "orbit-4104/bkg_cam1_spm1_1208878859.cal.fits")

    Returns
    -------
    x, y, z, ok :
        The x coordinate, the y coordinate, the image, mask of the good data.

    '''


    hdu = fits.open(filename)
    z = hdu[0].data
    rows, columns = z.shape
    x1d = np.arange(columns) - columns/2
    y1d = np.arange(rows) - rows/2
    x, y = np.meshgrid(x1d, y1d)

    # faus set the chip gaps to 0
    ok = z != 0

    return x, y, z, ok

def test(**kw):
    '''
    Test out the model fitting on a test image.
    '''

    # create a fake test image
    x, y, z, ok, truth = create_test_image(**kw)

    # throw out the corners (flux values of exactly 0 are ignored)
    r = np.sqrt(x**2 + y**2)
    incircle = r < np.max(x)
    ok *= incircle
    #z[incircle == False] = 0

    # make an initial guess model
    initial = guess_2d_gaussian(x,y,z)

    # fit it (binning by 100)
    fitted = fit_model(x, y, z, model=initial)

    #plot_fit(xsmall, ysmall, zsmall, truth)
    plot_fit(x, y, z, ok, models=[fitted, initial, truth], colors=['darkorchid', 'gray', 'hotpink'])


def fit_camera(filename):
    '''
    Fit an image from a full camera.
    '''

    # load an image from a FITS file
    x, y, z, ok = load_camera(filename)

    # throw out the corners
    r = np.sqrt(x**2 + y**2)
    ok *= r < np.max(x)*1.2

    # make an initial guess model
    initial = guess_2d_gaussian(x,y,z)

    # fit it (binning by 100)
    fitted = fit_model(x, y, z, model=initial)

    #plot_fit(xsmall, ysmall, zsmall, truth)
    plot_fit(x, y, z, ok, models=[fitted, initial], colors=['darkorchid', 'gray'])
