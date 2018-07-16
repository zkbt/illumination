from .imshowFrame import *
from astropy.nddata.utils import Cutout2D

class ZoomFrame(imshowFrame):
	frametype = 'Zoom'
	def __init__(self, source, position=(0,0), size=(10,10), **kwargs):
		'''
		Initialize a ZoomFrame that can display
		images taken from a zoomed subset of
		a `source` imshowFrame. This is kind
		of like a magnifying class you can
		drop down on an image.

		Parameters
		----------

		source : imshowFrame
			A frame into which this one will be zooming.

		position : (tuple)
			The (x, y) = (col, row) position of the center of zoom.

		shape : (tuple)
			The (x, y) = (ncols, nrows) shape of the zoom.
		'''

		FrameBase.__init__(self,  **kwargs)

		self.source = source
		self.position = position
		self.size = size

		# tidy up the axes for this camera
		self.ax.set_aspect('equal')
		plt.setp(self.ax.get_xticklabels(), visible=False)
		plt.setp(self.ax.get_yticklabels(), visible=False)
		#self.ax.set_facecolor('black')

		self.titlefordisplay =  '{} | {}'.format(self.frametype, self.position)

	def _gettimes(self):
		'''
		Get the available times associated with this frame.
		'''
		return self.source._gettimes()

	#def _timestring(self, time):
	#	'''
	#	Return a string, given an input time (still in spacecraft time).
	#	'''
	#	return  't={}'.format(time)

	def _find_timestep(self, time):
		'''
		Get the timestep, by using the source frame.
		'''
		return self.source._find_timestep(time)

	def _get_image(self, time=None):
		'''
		Get the image at a given time (defaulting to the first time),
		by pulling it from the source frame.
		'''

		bigimage, actual_time = self.source._get_image(time)
		self.cutout = Cutout2D(bigimage, self.position, self.size, mode='partial')
		cutoutimage = self.cutout.data
		return cutoutimage, actual_time

	def plot(self, *args, **kwargs):
		imshowFrame.plot(self, *args, **kwargs)

		# add a box to the source image (cutout must have ben created, if plot has happened)
		self.cutout.plot_on_original(ax=self.source.ax, clip_on=True)

	def update(self, time):
		'''
		Update this frame to a particular time (for use in animations).
		'''
		# update the data, if we need to
		timestep = self._find_timestep(time)
		image, actual_time = self._get_image(time)
		if image is None:
			return

		if timestep != self.currenttimestep:
			self.plotted['imshow'].set_data(image)
			self.plotted['text'].set_text(self._timestring(actual_time))
