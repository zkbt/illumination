'''
This scripts makes some movies of the Mars encounter
at the end of commissioning.
'''
from playground.tv import *

fps = 6

code = '_diff_crop'
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]
i = illustratefits(files, ext_image=0, cmapkw=dict(vmax=1e4))
i.figure.set_figheight(5)
i.figure.set_figwidth(8)
i.plot()
i.frames['camera'].plotted['text'].set_visible(False)
animate(i, fps=fps, cadence=1*u.s, filename='mars-dehoc{}.mp4'.format(code.replace('_', '-')), dpi=300)


code = '_diff'
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]
i = illustratefits(files, ext_image=0)
i.plot()
i.frames['camera'].plotted['text'].set_visible(False)
animate(i, fps=fps, cadence=1*u.s, filename='mars-dehoc{}.mp4'.format(code.replace('_', '-')), dpi=500)


code = ''
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]

i = illustratefits(files, ext_image=0)
i.plot()
i.frames['camera'].plotted['text'].set_visible(False)
animate(i, fps=fps, cadence=1*u.s, filename='mars-dehoc{}.mp4'.format(code.replace('_', '-')), dpi=500)
