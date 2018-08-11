from playground.tv import *
orbit = 9

# make a movie of each CCD
#for camera in [1, 2, 3, 4]:
#    for ccd in [1, 2, 3, 4]:

camera = 1
ccd = 1
directory = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/FITS'.format(**locals*())
pattern = os.path.join(directory, 'tess*-*-{camera}-crm-ffi-ccd{ccd}.fits'.format(**locals())

i = illustratefits(pattern=cadence,
                   ext_image=0)
i.plot()
i.savefig('qlp-orbit-{}-cam{}-ccd{}.pdf'.format(orbit, camera, ccd), dpi=1000)
i.animate(filename=filename.replace('.pdf', '.mp4'),
          dpi=600,
          cadence=1 * u.s)  # chelsea's FFIs have no time, so use 1s
