from __future__ import print_function
from ..imports import *

def get_writer(filename, fps=30):
	'''
	Try to get an appropriate writer,
	given the filename provided.
	'''
	if '.mp4' in filename:
		try:
			writer = ani.writers['ffmpeg'](fps=fps)
		except (RuntimeError,KeyError):
			raise RuntimeError('This computer seems unable to ffmpeg.')
	else:
		try:
			writer = ani.writers['pillow'](fps=fps)
		except (RuntimeError, KeyError):
			writer = ani.writers['imagemagick'](fps=fps)
	return writer

def animate(illustration, filename='test.mp4',
			mintime=None, maxtimespan=None,
			fps=10, dpi=None, round=2, **kw):
	'''
	Create an animation from an Illustration,
	using the time axes associated with each frame.

	The Illustration needs to have been plotted once already.
	'''


	# figure out the times to display
	actualtimes, cadence = illustration._timesandcadence(round=round)

	lower, upper = min(actualtimes), max(actualtimes) + cadence

	if mintime is not None:
		lower = mintime
	if maxtimespan is not None:
		upper = lower + maxtimespan

	times = np.arange(lower, upper, cadence)
	print('animating {} times at {}s cadence for {}'.format(len(times), cadence, illustration))

	# get the writer
	writer = get_writer(filename, fps=fps)

	print(' to be saved at {}'.format(filename))
	# set up the animation writer
	with writer.saving(illustration.figure, filename, dpi or illustration.figure.get_dpi()):

		for i, t in enumerate(times):
			print('  {}/{} at {}'.format(i+1, len(times), Time.now().iso), end='\r')
			
			# update the illustration to a new time
			illustration.update(t)

			writer.grab_frame()
