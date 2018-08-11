from playground.tv import *
orbit = 9

# make a movie of each CCD
#for camera in [1, 2, 3, 4]:
#    for ccd in [1, 2, 3, 4]:

camera = 1
ccd = 1
directory = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/FITS'.format(**locals())
pattern = os.path.join(directory, 'tess*-*-{camera}-crm-ffi-ccd{ccd}.fits'.format(**locals()))
files = np.sort(glob.glob(pattern))[0:10]

sequence = make_sequence(files, ext_image=0, use_headers=False, use_filenames=True, timekey='cadence')

i = CCDIllustration(data=sequence)
i.plot()
filename = 'qlp-orbit-{}-cam{}-ccd{}.pdf'.format(orbit, camera, ccd)
i.savefig(filename, dpi=1000)
i.animate(filename=filename.replace('.pdf', '.mp4'),
          dpi=600,
          cadence=1 * u.s)  # chelsea's FFIs have no time, so use 1s



i = CCDIllustration(data=sequence)
for f in i.frames.values():
    f.processingsteps = ['subtractmean']

i.plot()
filename = 'difference-qlp-orbit-{}-cam{}-ccd{}.pdf'.format(orbit, camera, ccd)
i.savefig(filename, dpi=1000)
i.animate(filename=filename.replace('.pdf', '.mp4'),
          dpi=600,
          cadence=1 * u.s)
