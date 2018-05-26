from .FrameBase import *
from ..colors import cmap_norm_ticks
from ..sequence import make_sequence

class imshowFrame(FrameBase):

	frametype = 'imshow'
	xmin, xmax = None, None
	ymin, ymax = None, None
	def __init__(self, *args, **kwargs):
		FrameBase.__init__(self, *args, **kwargs)

		# if the data re that the data are a sequence of images
		self.data = make_sequence(self.data, **kwargs)

		# if there's an image, use it to set the size
		try:
			self.ymax, self.xmax = self.data[0].shape
		except IndexError:
			pass

		try:
			self.titlefordisplay =  self.data.titlefordisplay
		except AttributeError:
			self.titlefordisplay =  ''

	def _cmap_norm_ticks(self, *args, **kwargs):
		ill = self.illustration
		try:
			return ill.cmap, ill.norm, ill.ticks
		except AttributeError:
			self.cmap, self.norm, self.ticks = cmap_norm_ticks(*args, **kwargs)
			if self.illustration.sharecolorbar:
				self.illustration.cmap = self.cmap
				self.illustration.norm = self.norm
				self.illustration.ticks = self.ticks
			return self.cmap, self.norm, self.ticks


	def plot(self, timestep=0, clean=True, **kwargs):
		'''
		Make an imshow of a single frame of the cube.
		'''

		# make sure we point back at this frame
		plt.sca(self.ax)
		if clean:
			plt.cla()

		# pull out the array to work on
		image, actual_time = self._get_image()
		if image is None:
			plt.xlim(self.xmin, self.xmax)
			plt.ylim(self.ymin, self.ymax)
			return
		cmap, norm, ticks = self._cmap_norm_ticks(image)

		# display the image for this frame
		extent = [0, image.shape[1], 0, image.shape[0]]
		imshowed = self.ax.imshow(image, interpolation='nearest', origin='lower', norm=norm, cmap=cmap)

		# pull the title from the cube object (it can do some math)
		plt.title(self.titlefordisplay)

		# turn the axes lines off
		plt.axis('off')

		# add a colorbar
		neednewcolorbar = True
		if self.illustration is not None:
			if self.illustration.sharecolorbar:
				try:
					colorbarred = self.illustration.colorbar
					neednewcolorbar = False
				except AttributeError:
					pass
		if neednewcolorbar:
			try:
				assert(self.illustration.sharecolorbar)
				axes = [f.ax for f in self.illustration.frames.values() if f.ax is not None]
			except (AttributeError, AssertionError):
				axes = self.ax
			colorbarred = plt.colorbar(imshowed, ax=axes, orientation='horizontal', label=self.data.colorbarlabelfordisplay, fraction=0.04, pad=0.07, ticks=ticks)
			colorbarred.ax.set_xticklabels(['{:.0f}'.format(v) for v in ticks])
			colorbarred.outline.set_visible(False)
			self.illustration.colorbar = colorbarred

		# add a time label
		texted = self.ax.text(0.02, -0.02, self._timestring(self._gettimes()[timestep]), va='top', zorder=1e6, transform=self.ax.transAxes)

		# store the things that were plotted, so they can be updated
		self.plotted = dict(imshow=imshowed, text=texted)#, colorbar=colorbarred)

		# keep track of the current plotted timestep
		self.currenttimestep = timestep

		plt.xlim(self.xmin, self.xmax)
		plt.ylim(self.ymin, self.ymax)

	def _timestring(self, time):
		'''
		Return a string, given an input time (still in spacecraft time).
		'''
		try:
			offset = np.min(self.illustration._gettimes())
		except AttributeError:
			print('no illustration times found!')
			offset=0

		return 't={}{:+.3f}'.format(offset, time-offset)

	def _get_image(self, time=None):
		'''
		Get the image at a given time (defaulting to the first time).
		'''

		try:
			if time is None:
				time = self._gettimes()[0]
			timestep = self._find_timestep(time)
			image = self._transformimage(self.data[timestep])
			actual_time = self._gettimes()[timestep]
		except IndexError:
			return None, None
		return image, actual_time


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
