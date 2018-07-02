from ...imports import *

class FrameBase:

	data = None
	plotted = None
	frametype = 'base'

	def __init__(self, ax=None, data=None, framename='', illustration=None, aspectratio=1, **kwargs):
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
		framename : str
			A name to give this Frame.
		'''

		# assign this frame an axes to sit in
		self.ax = ax

		# this is likely a Sequence of some kind
		self.data = data

		# is there another overarching frame this one should be aware of?
		self.illustration = illustration

		# what is the intrinsic aspect ratio of this frame?
		self.aspectratio = aspectratio

		# keep track of a list of frames included in this one
		self.includes = []

		self._currenttimestring = None

	@property
	def offset(self):
		try:
			return self._offset
		except AttributeError:
			try:
				self._offset = np.min(self.illustration._gettimes().jd)
			except AttributeError:
				self._offset = np.min(self._gettimes().jd)#Time(0, format='jd')
			return self._offset

	def _timestring(self, time):
		'''
		Return a string, given an input time (still in spacecraft time).
		'''
		return 't={:.5f}{:+.5f}'.format(self.offset, time.jd-self.offset)

	def __repr__(self):
		return '<{} Frame | {}>'.format(self.frametype, self.data)

	def plot(self):
		'''
		This should be redefined in a class that inherits from FrameBase.
		'''
		raise RuntimeError("Don't know how to `plot` {}".format(self.frametype))

	def update(self, *args, **kwargs):
		'''
		This should be redefined in a class that inherits from FrameBase.
		'''
		raise RuntimeError("Don't know how to `update` {}".format(self.frametype))

	def _find_timestep(self, time):
		'''
		Given a time, identify its index.
		'''
		return self.data._find_timestep(time)

	def _gettimes(self):
		'''
		Get the available times associated with this frame.
		'''
		return self.data.time

	def _timesandcadence(self, round=None):
		'''
		Get all the unique times available across all the frames,
		along with a suggested cadence set by the minimum
		(rounded) differences between times.

		Parameters
		----------
		round : float
			All times will be rounded to this value.
			Times separated by less than this value
			will be considered identical.
		'''

		# store this calculation with the illustration, so it doesn't need repeating
		try:
			self._precaculatedtimesandcadence
		except AttributeError:
			self._precaculatedtimesandcadence = {}
		try:
			times, cadence = self._precaculatedtimesandcadence[round]
		except KeyError:
			alltimes = self._gettimes()

			if round is None:
				diffs = np.diff(np.sort(alltimes))
				round = np.min(diffs[diffs > 0])
			baseline = np.min(alltimes)
			rounded = round*np.round(np.array(alltimes-baseline)/round) + baseline
			times = np.unique(rounded)
			cadence = np.min(np.diff(times))
			self._precaculatedtimesandcadence[round] = times, cadence
		return times, cadence

	def _transformimage(self, image):
		'''
		Some frames will want to flip or rotate an image before display.
		This handles that transformation. (This should probably be set
		up as an matplotlib.axes transform type of thing.)
		'''
		return image


	def _transformxy(self, x, y):
		'''
		This handles the same transformation as that which goes into
		transform image, but for x and y arrays.
		'''
		return x, y

	def _get_orientation(self):
		'''
		Figure out the orientation of the overarching illustration.
		'''
		try:
			return self.illustration.orientation
		except:
			return 'vertical'
