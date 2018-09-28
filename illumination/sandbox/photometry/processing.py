from .visualize import *
from ...imports import *
from ...postage import *

def bin_jitter(lc, binwidth=30.0/60./24, robust=False):
    '''
    Bin the jitter to a useful cadence.
    '''

    c, r = lc.centroid_col, lc.centroid_row

    #bx, by, be = binto(lc.time, np.sqrt(c**2 + r**2), binwidth=binwidth, sem=False, robust=True)
    #plt.bar(bx, be, width=binwidth, alpha=0.3, label='radial')

    time, ry, re = binto(lc.time, r, binwidth=binwidth, sem=False, robust=False)
    _, cy, ce = binto(lc.time, c, binwidth=binwidth, sem=False, robust=False)


    centroid_col = cy - np.nanmedian(cy)
    centroid_row = ry - np.nanmedian(ry)
    intrajitter_col = ce
    intrajitter_row = re
    return time, centroid_col, centroid_row, intrajitter_col, intrajitter_row


def change_pipeline_aperture(tpf, aperture, backgroundaperture):
    tpf.hdu[-1].data = np.maximum(3*aperture, 2*backgroundaperture)

def define_apertures(tpf,  apertureradius=3, searchradius=5, backgroundpercentile=20, visualize=True):

    # make a stacked image of this stamp
    image = np.mean(tpf.flux, 0)

    # identify which pixels we want to call the background
    backgroundaperture = image <= np.percentile(image, backgroundpercentile)
    image -= np.mean(image[backgroundaperture])

    # create a search circle at the center of the stamp
    col, row = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    rcenter, ccenter = np.mean(row), np.mean(col)
    incircle = np.sqrt((row-rcenter)**2 + (col-ccenter)**2) < searchradius

    # find the flux-weighted centroid within that search circle
    rcentroid = np.sum(row*image*incircle)/np.sum(image*incircle)
    ccentroid = np.sum(col*image*incircle)/np.sum(image*incircle)

    # define the aperture
    aperture = np.sqrt((row-rcentroid)**2 + (col-ccentroid)**2) < apertureradius

    # actually apply the changes to the tpf
    change_pipeline_aperture(tpf, aperture, backgroundaperture)

    return aperture, backgroundaperture

def subtract_background(tpf):

    backgroundaperture = tpf.hdu[-1].data == 2
    background1d = np.median(tpf.hdu[1].data['RAW_CNTS'][:, backgroundaperture], 1)

    # store the background in the FITS
    tpf.hdu[1].data['FLUX_BKG'][:,:,:] = background1d[:, np.newaxis, np.newaxis]
    tpf.hdu[1].data['FLUX'] = tpf.hdu[1].data['RAW_CNTS'] - tpf.hdu[1].data['FLUX_BKG']

    #if visualize:
    #    pass
    #    #ax = tpf.to_lightcurve().plot(normalize=False, label='target')
    #    plt.plot(background1d*np.sum(tpf.pipeline_mask), label='background')
    #    plt.plot(np.sum(tpf.hdu[1].data['RAW_CNTS'][:, tpf.pipeline_mask], 1), label='total')

        #plt.legend()
        #plt.show()

def stamps_to_tpfs(files, tpfdirectory='.', **kw):
    '''
    Take a list of .npy stamp files,
    and convert them to TPFs.
    '''
    for f in files:
        print('converting {} into a proper TPF'.format(f))
        s = Stamp(f)
        tpf = EarlyTessTargetPixelFile.from_stamp(s)
        print('saving {} to {}'.format(tpf, tpfdirectory))
        tpf.to_fits(directory=tpfdirectory, **kw)


def photometer(tpf, **kw):

    # set the apertures
    define_apertures(tpf, **kw)

    # subtract the background from the flux array
    subtract_background(tpf)

    lc = tpf.to_lightcurve('pipeline')
    return lc

def calculate_differences(tpf, **kw):
    '''
    Make a copy of a TPF that is populated with time-differences.
    '''

    differenced = copy.deepcopy(tpf)

    differenced.hdu[1].data['FLUX'][:-1,:,:] = np.diff(tpf.flux, axis=0)
    differenced.hdu[1].data['FLUX'][-1,:,:] = 0

    #differenced.hdu[1].data['FLUX'][0,:,:] = 0#np.nan

    return differenced

def calculate_gradients(image, visualize=False):
    '''
    Make the 2D image gradients of the image.

    Parameters
    ----------

    image : 2D array
        For example, a median-stacked image.

    Returns
    -------

    dMdx_forward, dMdy_forward, dMdx_forward, dMdy_backward : 2D arrays
        Each the same size as the original image,
        containing the image gradient components.
    '''
    dMdx_forward, dMdx_backward, dMdy_forward, dMdy_backward = [np.zeros_like(image) for _ in range(4)]
    dMdx_forward[:,:-1] = np.diff(image, axis=1)
    dMdx_backward[:,1:] = np.diff(image, axis=1)
    dMdy_forward[:-1,:] = np.diff(image, axis=0)
    dMdy_backward[1::] = np.diff(image, axis=0)

    if visualize:
        fi, ax = plt.subplots(4, 2, sharex=True, sharey=True, figsize=(3,7))
        grady, gradx = np.gradient(image)# np.diff(image[::-1], axis=1)[::-1]
        kw = dict(origin='lower')
        ax[0,0].imshow(image, **kw)
        ax[0,1].set_visible(False)
        ax[1,0].imshow(dMdx_forward, **kw)
        ax[2,0].imshow(dMdx_backward, **kw)
        ax[3,0].imshow(gradx, **kw)

        ax[1,1].imshow(dMdy_forward, **kw)
        ax[2,1].imshow(dMdy_backward, **kw)
        ax[3,1].imshow(grady, **kw)

        ax[1,0].set_ylabel('forward')
        ax[2,0].set_ylabel('backward')
        ax[3,0].set_ylabel('threepix')

        ax[3,0].set_xlabel('x'); ax[3,1].set_xlabel('y')
    return dMdx_forward, dMdy_forward, dMdx_forward, dMdy_backward




# NEXT STEPS
# -compare light curves with/without CRM
# -plot and do photometry on differences between +/- CRM
#
