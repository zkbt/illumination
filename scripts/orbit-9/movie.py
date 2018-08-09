from playground.tv import *
orbit = 9
directory = '/pdo/ramp/orbit-{}/ffi_fits'.format(orbit)
def camera_from_filename(f):
    '''
    A function to return the camera of a file, given its filename.
    '''
    try:
        return os.path.basename(f).split('-')[2]
    except IndexError:
        return '?'

# make a movie of the four cameras
i = illustratefits(pattern='/pdo/ramp/orbit-9/ffi_fits/tess*-*-*-crm-ffi_dehoc.fits', ext_image=0, get_camera=camera_from_filename)
i.plot()
filename = 'orbit-{}-four-camera-illustrated.pdf'.format(orbit)
plt.savefig(filename, dpi=300)
print("saved to {}".format(filename))
animate(i, filename=filename.replace('.pdf', '.mp4'), dpi=300, cadence=30*u.minute) # dehocs have no time, so use 1s

# make a movie of each camera
for c in [1,2,3,4]:
    i = illustratefits(pattern='/pdo/ramp/orbit-9/ffi_fits/tess*-*-{}-crm-ffi_dehoc.fits'.format(c), ext_image=0, get_camera=camera_from_filename)
    filename = 'orbit-{}-camera-{}-illustrated.pdf'.format(orbit, c)
    plt.savefig(filename, dpi=300)
    print("saved to {}".format(filename))
    animate(i, filename=filename.replace('.pdf', '.mp4'), dpi=300, cadence=30*u.minute) # dehocs have no time, so use 1s

# make a movie of each CCD
for camera in [1,2,3,4]:
    for ccd in [1,2,3,4]:
        i = illustratefits(pattern='/pdo/ramp/orbit-9/cal_ffi/tess*-*-{camera}-crm-ffi_ccd{ccd}.cal.fits'.format(camera=camera, ccd=ccd), ext_image=0, get_camera=camera_from_filename)
        filename = 'orbit-{}-camera-{}-ccd-{}-illustrated.pdf'.format(orbit, camera, ccd)
        plt.savefig(filename, dpi=300)
        print("saved to {}".format(filename))
        animate(i, filename=filename.replace('.pdf', '.mp4'), dpi=300, cadence=30*u.minute) # dehocs have no time, so use 1s



# make a movie of each CCD
