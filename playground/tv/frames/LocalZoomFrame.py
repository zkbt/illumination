from .imshowFrame import *
from astropy.nddata.utils import Cutout2D
from matplotlib.patches import Rectangle

class LocalZoomFrame(imshowFrame):
	frametype = 'Zoom'
	def __init__(self, source, position=(0,0), size=(10,10), zoom=10, **kwargs):
		'''
		Initialize a ZoomFrame that can display
		images taken from a zoomed subset of
		a `source` imshowFrame. This is kind
		of like a magnifying class you can
		drop down on an image.

		It *doesn't* add a new axis.

		Parameters
		----------

		source : imshowFrame
			A frame into which this one will be zooming.

		position : (tuple)
			The (x, y) = (col, row) position of the center of zoom.
			(These are in original image coordinates,
			not those that have been transformed for display.)

		shape : (tuple)
			The (x, y) = (ncols, nrows) shape of the zoom.
		'''

		FrameBase.__init__(self,  **kwargs)

		#
		self.source = source
		self.source.includes.append(self)

		self.position = position
		self.size = size
		self.zoom =zoom

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

		# get the image, transform to the rotated camera frame
		transformedbigimage, actual_time = self.source._get_image(time)

		# get the position of this stamp, transformed to the rotated camera frame
		transformedxy = self.source._transformxy(*self.position)
		self.cutout = Cutout2D(transformedbigimage, transformedxy, self.size, mode='partial')

		# all coordinates for the cutout are now in the transformed coordinates
		cutoutimage = self.cutout.data
		return cutoutimage, actual_time

	def plot(self, timestep=0, **kwargs):

		image, actual_time = self._get_image()
		cmap, norm, ticks = self.source._cmap_norm_ticks(image)


		# these are in the rotated camera frame
		x, y = self.cutout.center_original
		ysize, xsize = self.cutout.shape

		left, right = x - xsize*self.zoom/2, x + xsize*self.zoom/2
		bottom, top = y - ysize*self.zoom/2, y + ysize*self.zoom/2

		extent = [left, right, bottom, top]


		zooms = [self.illustration.frames[k] for k in self.illustration.frames.keys() if 'zoom' in k]
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

			timestring = self.source._timestring(actual_time)
			if self.source._currenttimestring != timestring:
				self.source.plotted['text'].set_text(timestring)
				self.source._currenttimestring = timestring
