# import the tv tools
from playground.tv import *

# collect the files we want
orbit = 9
pattern = '/pdo/ramp/orbit-{}/ffi_fits/tess*-000*-*-crm-ffi_dehoc.fits'.format(orbit)
files = glob.glob(pattern)

# make an illustration of the four camers
i = illustratefits(files, processingsteps=['subtractmean'])

# animate that illustration
i.animate(filename='diff-orbit{}-four-camera.mp4'.format(orbit),
          dpi=300,
          cadence=1 * u.s)  # dehocs have no time, so use 1s as a kludge
