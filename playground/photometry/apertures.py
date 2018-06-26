from ..imports import *

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

    if visualize:
        fi, ax = plt.subplots(1,3,figsize=(10, 2), sharex=True,sharey=True)
        frame = int(len(tpf.time)/2)
        tpf.plot(ax[0], frame=frame)
        tpf.plot(ax[1], aperture_mask=tpf.hdu[-1].data == 3, frame=frame)
        ax[1].set_title('target')
        tpf.plot(ax[2], aperture_mask=tpf.hdu[-1].data == 2, frame=frame)
        ax[2].set_title('background')

        #plt.imshow(image)
        #plt.colorbar()
        plt.scatter(ccentroid, rcentroid, zorder=100)


    return aperture, backgroundaperture

def subtract_background(tpf):

    backgroundaperture = tpf.hdu[-1].data == 2
    background1d = np.median(tpf.flux[:, backgroundaperture], 1)

    # store the background in the FITS
    tpf.hdu[1].data['FLUX_BKG'][:,:,:] = background1d[:, np.newaxis, np.newaxis]
    tpf.hdu[1].data['FLUX'] = tpf.hdu[1].data['RAW_CNTS'] - tpf.hdu[1].data['FLUX_BKG']


# NEXT STEPS
# -compare light curves with/without CRM
# -plot and do photometry on differences between +/- CRM
#
