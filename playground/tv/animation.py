from __future__ import print_function
from .imports import *

def get_writer(filename, fps=30):
	'''
	Try to get an appropriate writer,
	given the filename provided.
	'''
	if '.mp4' in filename:
		writer = ani.writers['ffmpeg'](fps=fps)
	else:
		try:
			writer = ani.writers['pillow'](fps=fps)
		except (RuntimeError, KeyError):
			writer = ani.writers['imagemagick'](fps=fps)
	return writer

def animate(illustration, filename='test.mp4',
			maxtimespan=None,
			fps=30, dpi=None, **kw):
	'''
	Create an animation from an Illustration,
	using the time axes associated with each frame.
	'''

	# figure out the times to display
	actualtimes, cadence = illustration._timesandcadence()

	lower, upper = min(actualtimes), max(actualtimes) + cadence
	if maxtimespan is not None:
		upper = lower + maxtimespan

	times = np.arange(lower, upper, cadence)
	print('animating {} times at {}s cadence for {}'.format(len(times), cadence, illustration))

	# get the writer
	writer = get_writer(filename, fps=fps)

	# set up the animation writer
	with writer.saving(illustration.figure, filename, dpi or illustration.figure.get_dpi()):

		for i, t in enumerate(times):
			print(' finished {}/{} times'.format(i, len(times)), end='\r')

			# update the illustration to a new time
			illustration.update(t)

			writer.grab_frame()
