from playground.tv import *
orbit = 9

# make a movie of each CCD
#for camera in [1, 2, 3, 4]:
#    for ccd in [1, 2, 3, 4]:

for camera in [1,2,3,4]:
    sequences = {}
    for ccd in [1,2,3,4]:
        directory = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/FITS'.format(**locals())
        pattern = os.path.join(directory, 'tess*-*-{camera}-crm-ffi-ccd{ccd}.fits'.format(**locals()))
        files = list(np.sort(glob.glob(pattern)))
        sequence = make_sequence(files, ext_image=0, use_headers=False, use_filenames=True, timekey='cadence')

        # load a median image, instead of computing it
        medianfilename = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/sub/Median.fits'.format(**locals())
        sequence.spatial['median']  = fits.open(medianfilename)[0].data
        sequences['ccd{}'.format(ccd)] = sequence

    # make both a raw, and a differenced movie
    for difference in [True, False]:

        i = CameraOfCCDsIllustration(**sequences)
        if difference:
            for f in i.frames.values():
                f.processingsteps = ['subtractmedian']

        i.plot()
        filename = '{}qlp-orbit{}-cam{}.pdf'.format({True:'difference-', False:''}[difference], orbit, camera, ccd)
        i.savefig(filename, dpi=1200)
        i.animate(filename=filename.replace('pdf', 'mp4'), dpi=500)
