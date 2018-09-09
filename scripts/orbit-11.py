from playground.tv import *
# do normal and subtracted
for processingsteps in [[], ['subtractmean']]:
    # do grayscale and not
    for gray in [True, False]:
        # do short and long
        for N in [25, None]:
            # do three orbits
            for orbit in [11]:

                # base directory
                directory = '/pdo/poc-data/orbits/orbit-{}/ffi_fits'.format(orbit)


                # compile a dictionary of cameras, with a subdictionary of ccds
                cameras = {}
                for camera in [1,2,3,4]:

                        # pull out the files for this single CCD
                        filepattern = 'tess*-*-{camera}-crm-ffi.fits'
                        pattern = os.path.join(directory, filepattern.format(**locals()))
                        files = list(np.sort(glob.glob(pattern)))[:N]

                        # make a sequence out of these images
                        sequence = make_sequence(files, ext_image=0, use_headers=False, use_filenames=True, timekey='cadence')

                        cameras['cam{}'.format(camera)] = sequence

                # create an illustration
                i = FourCameras(processingsteps=processingsteps,
                                plotingredients=['image', 'time','colorbar'],
                                **cameras)
                if gray:
                    i.cmapkw['cmap'] = 'gray_r'
                if processingsteps == []:
                    i.cmapkw['vmin'] = 3e4
                    i.cmapkw['vmax'] = 1e6

                i.plot()
                filename = 'orbit{}-four-camera'.format(orbit)
                if gray:
                    filename += '-gray'
                if N is not None:
                    filename += '-limit-{}'.format(N)
                if len(processingsteps) > 0:
                    filename += '-{}'.format('-'.join(processingsteps))
                filename += '.pdf'
                i.savefig(filename, dpi=300)
                i.animate(filename.replace('pdf', 'mp4'), cadence=1.0*u.s)
