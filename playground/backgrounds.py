import warnings
import numpy as np
import matplotlib.pyplot as plt
from astropy.modeling import models, fitting
from matplotlib.patches import Ellipse

def create_test_image(gap=3, N=25):
    '''
    Create one random crudely-stitched camera, with a Gaussian-ish background to it.
    '''

    # generate a random model
    p_generate = (models.Const2D(amplitude=10**np.random.uniform(0, 1)) +
               models.Gaussian2D(amplitude=10**np.random.uniform(.5, 2),
                                   x_mean=np.random.uniform(-N, N),
                                   y_mean=np.random.uniform(-N, N),
                                   x_stddev=np.random.uniform(2, N),
                                   y_stddev=np.random.uniform(2, N),
                                   theta=np.random.uniform(0, 2*np.pi)))

    p_generate.x_stddev.fixed = True
    p_generate.y_stddev.fixed = True

    # create fake x and y arrays
    x, y = np.meshgrid(np.arange(-N-gap, N+gap+1), np.arange(-N-gap, N+gap+1))

    # create the model
    perfect = p_generate(x, y)
    z = np.random.normal(perfect, 1)

    # find the gaps and replace them with zeros
    bad = (np.abs(x) < gap) | (np.abs(y) < gap)
    z[bad] = 0

    return x, y, z, p_generate

def showimage(x, y, z, **kw):
    '''
    Use imshow to show all four CCDs.
    '''
    plt.imshow( z,
                origin='lower',
                extent=[np.min(x), np.max(x), np.min(y), np.max(y)],
                interpolation='nearest',
                **kw)
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

def fit_2d_gaussian(x, y, z,
                    imagebinning=1,
                    ignore=0,
                    baseline=10,
                    amplitude=10,
                    x_mean=0, y_mean=0,
                    x_stddev=500, y_stddev=500, theta=0,
                    **kw):
    '''
    Fit the scattered light in a list of images (with x, y, z) for each.

    Parameters
    ----------
    x, y, z : 2D arrays
        The x and y values of each pixel (kind of boring images), and the z flux of the image.
    imagebinning : int
        By how many pixels should the images be binned?
        This substantially speeds up fitting.
    ignore : float
        Ignore pixels that have a particular value.
        (e.g. Michael set the chip overscans to 0)
    (others) : float
        Initial guesses for the parameters of Gaussian2D

    '''

    # create an initial model, with the initial guesses
    p_init = (models.Const2D(amplitude=baseline) +
           models.Gaussian2D(amplitude=amplitude,
                               x_mean=x_mean, y_mean=y_mean,
                               x_stddev=x_stddev, y_stddev=y_stddev, theta=theta))

    # construct the fitter (using LM)
    fit_p = fitting.LevMarLSQFitter()

    # run the fit (skipping some warnings)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        # pull out only good data
        ok = z != ignore

        # if desired, bin the data
        if imagebinning == 1:
            bx, by, bz, bok = x, y, z, ok
        else:
            bx = bin_image(x, binning=imagebinning)
            by = bin_image(y, binning=imagebinning)
            bz = bin_image(z, binning=imagebinning)
            bok = bin_image(ok, binning=imagebinning) == 1

        # run the fit, starting with initial model and comparing to the data
        p = fit_p(p_init, bx[bok], by[bok], bz[bok])

    return p

def plot_2d_gaussian(p, **kw):
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
                      edgecolor='darkorchid', alpha=0.5, **kw)
    plt.gca().add_artist(ellipse)


def plot_fit(x, y, z, p, cmap='gray', **kw):
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

    plt.sca(ax[0])
    showimage(x, y, z, vmin=vmin, vmax=vmax, cmap=cmap, **kw)
    plot_2d_gaussian(p)
    plt.title("Data")

    plt.sca(ax[1])
    showimage(x, y, p(x,y), vmin=vmin, vmax=vmax, cmap=cmap, **kw)
    plot_2d_gaussian(p)
    plt.title("Model")

    plt.sca(ax[2])
    showimage(x, y, z-p(x,y), vmin=vmin, vmax=vmax, cmap=cmap, **kw)
    plot_2d_gaussian(p)
    plt.title("Residual")

def test():

    # create a fake test image
    x, y, z, truth = create_test_image(N=2048, gap=100)

    # fit it (binning by 100)
    p = fit_2d_gaussian(x, y, z, imagebinning=100)
    #plot_fit(xsmall, ysmall, zsmall, truth)
    plot_fit(x, y, z, p)
