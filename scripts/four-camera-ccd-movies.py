from playground.tv import *
for orbit in [9,10]:
    N = 3
    directory = '/pdo/ramp/orbit-{}/cal_ffi'.format(orbit)

    # compile a dictionary of cameras, with a subdictionary of ccds
    cameras = {}
    for camera in [1,2,3,4]:

        # include each CCD individually
        ccds = {}
        for ccd in [1,2,3,4]:


            # pull out the files for this single CCD
            filepattern = 'tess*-*-{camera}-crm-ffi_ccd{ccd}.cal.fits'
            pattern = os.path.join(directory, filepattern.format(**locals()))
            files = list(np.sort(glob.glob(pattern)))[:N]

            # make a sequence out of these images
            sequence = make_sequence(files, ext_image=0, use_headers=False, use_filenames=True, timekey='cadence')

            # load a median image, instead of computing it
            #medianfilename = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/sub/Median.fits'.format(**locals())
            #sequence.spatial['median']  = fits.open(medianfilename)[0].data

            ccds['ccd{}'.format(ccd)] = sequence
        cameras['cam{}'.format(camera)] = ccds


    i = FourCameraOfCCDsIllustration(processingsteps=['subtractmedian'],**cameras)
    i.plot()
    filename = 'subtracted-orbit{}-four-camera.pdf'.format(orbit)
    i.savefig(filename, dpi=300)
    i.animate(filename.replace('pdf', 'mp4'), cadence=1.0*u.s)

    # make both a raw, and a differenced movie
    for cam in cameras.keys():
        i = CameraOfCCDsIllustration(processingsteps=['subtractmedian'],**cameras[cam])
        i.plot()
        filename = 'subtracted-orbit{}-{}.pdf'.format(orbit, cam)
        i.savefig(filename, dpi=300)
        i.animate(filename.replace('pdf', 'mp4'), cadence=1.0*u.s)
