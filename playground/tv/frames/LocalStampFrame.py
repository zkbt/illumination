from .imshowFrame import *
from astropy.nddata.utils import Cutout2D
from matplotlib.patches import Rectangle
from .LocalZoomFrame import LocalZoomFrame

class LocalStampFrame(imshowFrame):
	'''
	This frame imshows a Stamp object
	at its appropriate location on
	some source CameraFrame.
	'''

	frametype = 'Stamp'
	def __init__(self, data, source, position=(0,0), zoom=10, **kwargs):
		'''
		Initialize a LocalStampFrame that can display
		images taken from a zoomed subset of
		a `source` imshowFrame. This is kind
		of like a magnifying class you can
		drop down on an image, but its data
		comes from a single stamp at a time.

		It *doesn't* add a new axis.

		Parameters
		----------

		data : Stamp
			A StampSequence that contains all its own data.

		source : imshowFrame
			A frame into which this one will be zooming.

		position : (tuple)
			The (x, y) = (col, row) position of the center of zoom.
			(These are in original image coordinates,
			not those that have been transformed for display.)

		'''

		imshowFrame.__init__(self,  data=data, **kwargs)

		self.source = source
		self.position = position
		self.zoom = zoom

		self.titlefordisplay =  '{} | {}'.format(self.frametype, self.position)

	def _gettimes(self):
		'''
		Get the available times associated with this frame.
		'''
		return self.data._gettimes()

	def _timestring(self, time):
		'''
		Return a string, given an input time (still in spacecraft time).
		'''
		return  't={}'.format(time)

	def _find_timestep(self, time):
		'''
		Get the timestep, by using the source frame.
		'''
		return self.data._find_timestep(time)

	def position_center(self):
		return self.data.col_cent
	def plot(self, timestep=0, **kwargs):

		image, actual_time = self._get_image()
		cmap, norm, ticks = self.source._cmap_norm_ticks(image)

		# KLUDGE! ZOOM AND STAMP SHOULD BE CONSISTENT!
		# these are in the rotated camera frame
		x, y = self.position #self.cutout.center_original
		ysize, xsize = self.data[0].shape

		left, right = x - xsize*self.zoom/2, x + xsize*self.zoom/2
		bottom, top = y - ysize*self.zoom/2, y + ysize*self.zoom/2

		extent = [left, right, bottom, top]

		# THIS IS ANOTHER DIFFERENCE!
		zooms = [self.illustration.frames[k] for k in self.illustration.frames.keys() if 'stamp' in k]
		zorder = zooms.index(self)

		imshowed = self.source.ax.imshow(image,
						extent=extent,
						interpolation='nearest',
						origin='lower',
						norm=norm, cmap=cmap,
						zorder=zorder)

		# Create a Rectangle patch
		rect = Rectangle((left, bottom), xsize*self.zoom,ysize*self.zoom,
				linewidth=1,edgecolor='black',facecolor='none',
				zorder=zorder+0.5, clip_on=True)

		# Add the patch to the Axes
		boxonzoom = self.source.ax.add_patch(rect)

		self.source.ax.set_clip_on(True)
		# add a box to the source image (cutout must have ben created, if plot has happened)
		#boxonoriginal = self.cutout.plot_on_original(ax=self.source.ax, clip_on=True)

		self.plotted = dict(imshow=imshowed, boxonzoom=boxonzoom)
		self.currenttimestep = timestep

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
			#self.plotted['text'].set_text(self._timestring(actual_time))
