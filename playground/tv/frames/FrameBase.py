from ...imports import *
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
			return np.flatnonzero(self._gettimes() <= time)[-1]
		except IndexError:
			return 0

	def _gettimes(self):
		'''
		Get the available times associated with this frame.
		'''
		return self.data.time
