from playground.tv import *


code = '_diff_crop'
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
i = illustratefits(files, ext_image=0)
i.figure.set_figheight(5)
i.figure.set_figwidth(8)
i.plot()
i.frames['camera'].plotted['text'].set_visible(False)
animate(i, fps=5, cadence=1*u.s, filename='mars-dehoc{}.mp4'.format(code), dpi=300)


code = '_diff'
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
i = illustratefits(files, ext_image=0)
i.plot()
i.frames['camera'].plotted['text'].set_visible(False)
animate(i, cadence=1*u.s, filename='mars-dehoc{}.mp4'.format(code), dpi=500)


code = ''
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
i = illustratefits(files, ext_image=0)
i.plot()
i.frames['camera'].plotted['text'].set_visible(False)
animate(i, cadence=1*u.s, filename='mars-dehoc{}.mp4'.format(code), dpi=500)
