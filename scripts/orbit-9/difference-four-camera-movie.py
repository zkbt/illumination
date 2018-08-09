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
i = illustratefits(pattern='/pdo/ramp/orbit-9/ffi_fits/tess*-*-*-crm-ffi_dehoc.fits',
                   ext_image=0, get_camera=camera_from_filename)
for f in i.frames.items():
    f.processingsteps = ['subtractmedian']
i.plot()
filename = 'orbit-{}-four-camera-illustrated.pdf'.format(orbit)
plt.savefig(filename, dpi=1000)
print("saved to {}".format(filename))
animate(i, filename=filename.replace('.pdf', '.mp4'), dpi=300,
        cadence=1 * u.s)  # dehocs have no time, so use 1s
