'''
This script makes some movies of the Mars encounter
at the end of commissioning.
'''
from playground.tv import *

fps = 5

code = '_diff_crop'
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]
i = illustratefits(files, ext_image=0, cmapkw=dict(vmax=3e4, howmanysigmaarelinear=8))
i.figure.set_figheight(5)
i.figure.set_figwidth(8)
i.plot()
i.frames['camera'].plotted['time'].set_visible(False)
i.animate(fps=fps, cadence=1*u.s, filename='mars{}-fps{}.mp4'.format(code.replace('_', '-'), fps), dpi=300)


code = '_diff'
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]
i = illustratefits(files, ext_image=0)
i.plot()
i.frames['camera'].plotted['time'].set_visible(False)
i.animate(fps=fps, cadence=1*u.s, filename='mars{}-fps{}.mp4'.format(code.replace('_', '-'), fps), dpi=300)


code = ''
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]

i = illustratefits(files, ext_image=0)
i.plot()
i.frames['camera'].plotted['time'].set_visible(False)
i.animate(fps=fps, cadence=1*u.s, filename='mars{}-fps{}.mp4'.format(code.replace('_', '-'), fps), dpi=300)






from playground.tv import *
fps = 30
code = '_diff'
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]
i = illustratefits(files, ext_image=0, zoomposition=(400, 3800), zoomsize=(700, 700))
i.plot()
i.animate(fps=fps, cadence=1*u.s, filename='ghost-mars{}-fps{}.mp4'.format(code.replace('_', '-'), fps), dpi=300)


from playground.tv import *
fps = 30
code = ''
path = '/pdo/ramp/orbit-14348/cam*_dehoc{}.fits'.format(code)
files = list(np.sort(glob.glob(path)))
files = [f for f in files if '121650' not in f]
i = illustratefits(files, ext_image=0, zoomposition=(400, 3800), zoomsize=(700, 700))
i.plot()
i.animate(fps=fps, cadence=1*u.s, filename='ghost-mars{}-fps{}.mp4'.format(code.replace('_', '-'), fps), dpi=300)
