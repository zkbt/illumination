from playground.tv import *
orbit = 9

# make a movie of each CCD
#for camera in [1, 2, 3, 4]:
#    for ccd in [1, 2, 3, 4]:


# compile a dictionary of cameras, with a subdictionary of ccds
cameras = {}
for camera in [1,2,3,4]:

    # include each CCD inidividually
    ccds = {}
    for ccd in [1,2,3,4]:

        # pull out the files for this single CCD
        directory = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/FITS'.format(**locals())
        pattern = os.path.join(directory, 'tess*-*-{camera}-crm-ffi-ccd{ccd}.fits'.format(**locals()))
        files = list(np.sort(glob.glob(pattern)))


        sequence = make_sequence(files, ext_image=0, use_headers=False, use_filenames=True, timekey='cadence')

        # load a median image, instead of computing it
        medianfilename = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/sub/Median.fits'.format(**locals())
        sequence.spatial['median']  = fits.open(medianfilename)[0].data
        ccds['ccd{}'.format(ccd)] = sequence
    cameras['cam{}'.format(camera)] = ccds

# make both a raw, and a differenced movie
for difference in [False, True]:

    i = FourCameraIllustration(**cameras)
    if difference:
        for f in i.frames.values():
            f.processingsteps = ['subtractmedian']

    i.plot()
    filename = '{}qlp-orbit{}.pdf'.format({True:'difference-', False:''}[difference], orbit, camera, ccd)
    i.savefig(filename, dpi=1200)
    i.animate(filename=filename.replace('.pdf', '.mp4'),
              dpi=500,
              cadence=1 * u.s)  # chelsea's FFIs have no time, so use 1s
