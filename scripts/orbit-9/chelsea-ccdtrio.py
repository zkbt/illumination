from playground.tv import *
orbit = 9

# make a movie of each CCD
#for camera in [1, 2, 3, 4]:
#    for ccd in [1, 2, 3, 4]:

camera = 1
ccd = 1

patterns = {}
patterns['raw'] = '/pdo/ramp/orbit-9/cal_ffi/tess*-*-{camera}-crm-ffi_ccd{ccd}.cal.fits'.format(**locals())
patterns['qlp']= '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/FITS/tess*-*-{camera}-crm-ffi-ccd{ccd}.fits'.format(**locals())
patterns['subqlp'] = '/pdo/ramp/qlp_data/orbit-9/ffi/cam{camera}/ccd{ccd}/FITS/tess*-*-{camera}-crm-ffi-ccd{ccd}.fits'.format(**locals())

sequences = {}
for k in patterns.keys():
    sequences[k] = make_sequence(patterns[k], ext_image=0, use_headers=False, use_filenames=True, timekey='cadence')

raw = CCDFrame(data=sequences['raw'], title='Original Image')
normal = CCDFrame(data=sequences['qlp'], title='- Background')
subtracted = CCDFrame(data=sequences['subqlp'], title='- Median (background-subtracted) Image')

i = HybridIllustration(imshows=[raw, normal, subtracted], sharecolorbar=False)
i.plot()
filename = 'qlptrio-orbit-{}-cam{}-ccd{}.pdf'.format(orbit, camera, ccd)
i.savefig(filename, dpi=1200)
