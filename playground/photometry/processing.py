from ..imports import *
from .visualize import *
from ..postage import *

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
    differenced = copy.deepcopy(tpf)

    differenced.hdu[1].data['FLUX'][:-1,:,:] = np.diff(tpf.flux, axis=0)
    differenced.hdu[1].data['FLUX'][-1,:,:] = 0

    #differenced.hdu[1].data['FLUX'][0,:,:] = 0#np.nan

    return differenced

# NEXT STEPS
# -compare light curves with/without CRM
# -plot and do photometry on differences between +/- CRM
#
