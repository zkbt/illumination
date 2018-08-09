from playground.tv import *
orbit = 9
directory = '/pdo/ramp/orbit-{}/ffi_fits'.format(orbit)

# make a movie of each CCD
for camera in [1, 2, 3, 4]:
    for ccd in [1, 2, 3, 4]:
        i = illustratefits(pattern='/pdo/ramp/orbit-9/cal_ffi/tess*-*-{camera}-crm-ffi_ccd{ccd}.cal.fits'.format(
            camera=camera, ccd=ccd), ext_image=0, get_camera=camera_from_filename)
        i.plot()

        filename = 'orbit-{}-camera-{}-ccd-{}-illustrated.pdf'.format(
            orbit, camera, ccd)
        plt.savefig(filename, dpi=1000)
        print("saved to {}".format(filename))
        animate(i, filename=filename.replace('.pdf', '.mp4'), dpi=600,
                cadence=1 * u.s)  # dehocs have no time, so use 1s
