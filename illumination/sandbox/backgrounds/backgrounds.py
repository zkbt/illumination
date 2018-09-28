from ...imports import *

from astropy.modeling import models, fitting
from matplotlib.patches import Ellipse
from astropy.table import Table, vstack
from astropy.stats import SigmaClip
from photutils import Background2D, MedianBackground, SExtractorBackground


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

    # mask out the neglected pixels
    maskkw = dict(**imshowkw)
    maskkw['cmap'] = okcmap
    maskkw['vmin'] = 0
    maskkw['vmax'] = 1
    plt.imshow(ok, zorder=100, **maskkw)

    # show the image
    plt.imshow( z, zorder=-100, **imshowkw)
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
    vmin, vmax = np.percentile(z[ok], [1, 99])

    # plot the data with the best-fit model
    fi, ax = plt.subplots(1, 3, figsize=(10, 2.5), sharex=True, sharey=True)


    fitted = models[0]
    plt.sca(ax[0])
    showimage(x, y, z, ok, vmin=vmin, vmax=vmax, cmap=cmap, **kw)

    for m, c in zip(models, colors):
        plot_2d_gaussian(m, color=c)
    plt.axis('off')
    textkw = dict(color='white', alpha=0.5, weight='bold')
    plt.text(0.05, 0.05, 'data', transform=plt.gca().transAxes, **textkw)

    plt.sca(ax[1])
    showimage(x, y, fitted(x,y), ok, vmin=vmin, vmax=vmax, cmap=cmap, **kw)
    for m, c in zip(models, colors):
        plot_2d_gaussian(m, color=c)
    plt.axis('off')
    plt.text(0.05, 0.05, 'model', transform=plt.gca().transAxes, **textkw)


    plt.sca(ax[2])
    showimage(x, y, z-fitted(x,y), ok, vmin=vmin, vmax=vmax, cmap=cmap, **kw)
    for m, c in zip(models, colors):
        plot_2d_gaussian(m, color=c)
    plt.axis('off')
    plt.text(0.05, 0.05, 'residual', transform=plt.gca().transAxes, **textkw)

    plt.colorbar(ax=ax)

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
    fitted = fit_model(x, y, z, ok, model=initial)

    #plot_fit(xsmall, ysmall, zsmall, truth)
    plot_fit(x, y, z, ok, models=[fitted, initial, truth], colors=['darkorchid', 'gray', 'hotpink'])


def remove_stars_from_image(x, y, z, ok, box=150, filter=3, visualize=True, label=''):

    withstars = z
    sigma_clip = SigmaClip(sigma=3., iters=10)
    bkg_estimator = MedianBackground()#SExtractorBackground()#
    bkg = Background2D(withstars, box_size=(box,box), filter_size=(filter,filter), mask=ok==False,
                        sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)


    withoutstars = bkg.background*ok
    if visualize:

        fi, ax = plt.subplots(1, 3, figsize=(10,2.5), sharex=True, sharey=True)

        kw = dict(vmin=np.percentile(withoutstars, 2), vmax=np.percentile(withstars, 98), cmap='gray')
        textkw = dict(color='white', alpha=0.5, weight='bold')

        plt.sca(ax[0])
        showimage(x, y, z, ok, **kw)
        plt.text(0.05, 0.05, 'original', transform=plt.gca().transAxes, **textkw)
        plt.axis('off')

        plt.sca(ax[1])
        showimage(x, y, withoutstars, ok, **kw)
        plt.text(0.05, 0.05, 'background', transform=plt.gca().transAxes, **textkw)
        plt.axis('off')

        plt.sca(ax[2])
        showimage(x, y, withstars - withoutstars, ok, **kw)
        plt.text(0.05, 0.05, 'subtracted', transform=plt.gca().transAxes, **textkw)
        plt.axis('off')

        plt.suptitle(label)
        plt.colorbar(ax=ax)

    return withoutstars


def fit_camera(filename,
               binby=200,
               constrain_theta='clockhands',
               constrain_size=(100, 3000),
               visualize=True,
               label=None,
               removestars=False, **kw):
    '''
    Fit an image from a full camera.

    Parameters
    ----------

    filename : str
        Path to the FITS file for a full-camera stitched image.
    binby : int
        Factor by which to bin the image (speeds up fitting).
    constrain_theta : str or None
        'clockhands' means the angle rotates with location in the field
        None means the angle of the Gaussian is unconstrained
    constrain_size : 2-element tuple
        The min and max values for the widths of the blobs
    label : str
        How should files be saved?

    Returns:
    table : an astropy Table
        a single-row table of parameters for diffuse light fit

    '''

    if label is None:
        label = os.path.basename(filename).replace('.fits', '')

    fitfilename = 'fits/fit_{}.txt'.format(label)
    if os.path.exists(fitfilename):
        print("{} already exists -- not refitting.".format(fitfilename))
        row = ascii.read(fitfilename)
        return row

    # load an image from a FITS file
    x, y, z, ok = load_camera(filename)

    # throw out the corners
    r = np.sqrt(x**2 + y**2)
    ok *= r < np.max(x)

    # do we need to remove the stars from this image?
    if removestars:
        z = remove_stars_from_image(x, y, z, ok, visualize=visualize, label=label, **kw)
        if visualize:
            plotfilename = os.path.join('plots', 'background_{}.png'.format(label))
            plt.savefig(plotfilename, dpi=400)

    # make an initial guess model
    initial = guess_2d_gaussian(x,y,z)
    base, gauss = initial
    # should we make sure theta is is set by the position?
    if constrain_theta == 'clockhands':
        def tiedtheta(initial):
            '''
            Define theta from the clock position in the image.
            '''
            b, g = initial
            return np.arctan2(g.y_mean, g.x_mean)
        gauss.theta.tied = tiedtheta

    # should we set a typical size for the blob?
    if constrain_size:
        gauss.x_stddev.bounds = constrain_size
        gauss.y_stddev.bounds = constrain_size

    # fit it (binning by 100)
    fitted = fit_model(x, y, z, ok, model=initial, imagebinning=binby)


    if visualize:

        #plot_fit(xsmall, ysmall, zsmall, truth)
        plot_fit(x, y, z, ok, models=[fitted, initial], colors=['darkorchid', 'gray'])
        plt.suptitle(label)
        plotfilename = os.path.join('plots', 'fit_{}.png'.format(label))
        plt.savefig(plotfilename, dpi=400)


    b, g = fitted
    binitial, ginitial = initial
    imtype, camera, spm, time = label.split('_')#os.path.basename(filename).split('.')[0].split('_')
    d = dict(baseline=b.amplitude.value,
             amplitude=g.amplitude.value,
             x=g.x_mean.value,
             y=g.y_mean.value,
             radius=(g.x_mean.value**2 + g.y_mean.value**2),
             theta=g.theta.value,
             radial_width=g.x_stddev.value,
             theta_width=g.y_stddev.value,
             moment_x=ginitial.x_mean.value,
             moment_y=ginitial.y_mean.value,
             imtype=imtype,
             camera=camera,
             spm=spm,
             spacecrafttime=time,
             filename=os.path.basename(filename))

    row = Table([d], names=['baseline', 'amplitude', 'x', 'y', 'radius', 'theta', 'radial_width', 'theta_width', 'moment_x', 'moment_y', 'imtype', 'camera', 'spm', 'spacecrafttime', 'filename'])

    row.write(fitfilename, format='ascii.fixed_width', delimiter='|', bookend=False, overwrite=True)

    return row
