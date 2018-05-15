from .imports import *
from matplotlib.colors import SymLogNorm, LogNorm

class FrameBase:

	data = None
	plotted = None

	def __init__(self, ax=None, data=None, name=''):
		'''
		Initialize this frame,
		choosing the Axes in which it will display,
		and the setting data to be associated with it.

		Parameters
		----------

		ax : matplotlib.axes.Axes instance
			All plotting will happen inside this ax.
		data : flexible
			It can be custom object (e.g. a Stamp),
			or simple arrays, or a list of HDULists,
			or something else, depending on
			what this actual Frame does with it
			in `plot` and `update`.
		name : str
			A name to give this Frame.
		'''
		if ax is None:
			self.ax = plt.gca()
		else:
			self.ax = ax
		self.data = data
		self.name = name

	def plot(self):
		'''
		This should be redefined in a class that inherits from FrameBase.
		'''
		raise RuntimeError("Don't know how to `plot` {}".format(self.name))

	def update(self, *args, **kwargs):
		'''
		This should be redefined in a class that inherits from FrameBase.
		'''
		raise RuntimeError("Don't know how to `update` {}".format(self.name))

	def _findtimestep(self, time):
		'''
		Given a time, identify its index.
		'''
		try:
			return np.flatnonzero(self._gettimes() < time)[-1]
		except IndexError:
			return 0

	def _gettimes(self):
		'''
		Get the available times associated with this frame.
		'''
		return self.data.time

class imshowStampFrame(FrameBase):

	def plot(self, timestep=0, nsigma=1.0):
		'''
		Make an imshow of a single frame of the cube.
		'''

		# make sure we point back at this frame
		plt.sca(self.ax)

		# pull out the array to work on
		a = self.data.todisplay

		# figure out a decent color scale
		vmin, vmax = np.percentile(a, [1,99])
		# (probably move this to an inherited level, so we can share it?)
		if (a < 0).any():
			# go diverging, if this is a difference that crosses zero
			scale = np.maximum(np.abs(vmin), np.abs(vmax))
			vmin, vmax = -scale, scale
			span = np.log10(scale)
			whatfractionislinear = 0.1
			sigma = mad(a)

			norm = SymLogNorm(nsigma*sigma, linscale=span*whatfractionislinear, vmin=vmin, vmax=vmax)
			cmap = 'RdBu'
			ticks = [vmin, -nsigma*sigma, 0, nsigma*sigma, vmax]
		else:
			# go simple logarithmic, if this is all positive
			norm = LogNorm(vmin=vmin, vmax=vmax)
			cmap = 'Blues'
			ticks = [vmin, vmin*np.sqrt(vmax/vmin), vmax]

		# point at a particular image
		image = a[timestep, :,:]

		# display the image for this frame
		imshowed = plt.imshow(image, interpolation='nearest', origin='lower', norm=norm, cmap=cmap)

		# pull the title from the cube object (it can do some math)
		plt.title(self.data.titlefordisplay)

		# turn the axes lines off
		plt.axis('off')

		# add a colorbar
		colorbarred = plt.colorbar(imshowed, orientation='horizontal', label=self.data.colorbarlabelfordisplay, fraction=0.04, pad=0.02, ticks=ticks)
		colorbarred.ax.set_xticklabels(['{:.0f}'.format(v) for v in ticks])
		colorbarred.outline.set_visible(False)

		# add a time label
		texted = plt.text(0.05, 0.05, self._timestring(self._gettimes()[timestep]), transform=self.ax.transAxes)

		# store the things that were plotted, so they can be updated
		self.plotted = dict(imshow=imshowed, text=texted, colorbar=colorbarred)

		# keep track of the current plotted timestep
		self.currenttimestep = timestep

	def _timestring(self, time):
		return '{}s'.format(time)

	def update(self, time):
		'''
		Update this frame to a particular time (for use in animations).
		'''

		# update the data, if we need to
		timestep = self._findtimestep(time)
		if timestep != self.currenttimestep:
			self.plotted['imshow'].set_data(self.data.todisplay[timestep, :, :])
			self.plotted['text'].set_text(self._timestring(self._gettimes()[timestep]))
