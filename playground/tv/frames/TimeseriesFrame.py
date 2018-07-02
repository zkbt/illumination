from .FrameBase import *
from ..sequence import make_sequence

class TimeseriesFrame(FrameBase):

	frametype = 'timeseries'
	xmin, xmax = None, None
	ymin, ymax = None, None
	def __init__(self, *args, **kwargs):
		FrameBase.__init__(self, *args, **kwargs)

		# if the data re that the data are a sequence of images
		self.data = make_sequence(self.data, **kwargs)

		try:
			self.titlefordisplay =  self.data.titlefordisplay
		except AttributeError:
			self.titlefordisplay =  ''


	def plot(self, timestep=0, clean=False, **kwargs):
		'''
		Make an imshow of a single frame of the cube.
		'''

		self.plotted = {}

		# make sure we point back at this frame
		plt.sca(self.ax)

		# clean up by erasing this frame's axes
		if clean:
			plt.cla()

		# plot the time series
		time, y, yuncertainty = self.data.time.jd, self.data.y, self.data.yuncertainty
		x = time - self.offset

		if yuncertainty is None:
			self.plotted['timeseries'] = self.ax.plot(x, y, **kwargs)
		else:
			self.plotted['timeseries'] = self.ax.errorbar(x, y, yuncertainty, **kwargs)

		# pull out the time, add a vertical bar
		try:
			actual_time = self._gettimes()[timestep]
			timelabel = self._timestring(actual_time)
		except (ValueError, KeyError):
			actual_time = None
			timelabel = ''
		self.plotted['vline'] = plt.axvline(actual_time.jd - self.offset, color='gray', alpha=0.5, zorder=-1e6)

		# add a time label
		self.plotted['text'] = self.ax.text(0.01, +0.02, timelabel, va='bottom', zorder=1e6, transform=self.ax.transAxes)

		# pull the title for this frame
		plt.ylabel(self.titlefordisplay)
		if self.ax.get_xticklabels()[0].get_visible():
			plt.xlabel('Time - {:.5f} (days)'.format(self.offset))

		# turn the axes lines off
		# plt.axis('off')

		# keep track of the current plotted timestep
		self.currenttimestep = timestep

		plt.xlim(self.xmin, self.xmax)
		plt.ylim(self.ymin, self.ymax)

	"""
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
	"""
	def update(self, time):
		'''
		Update this frame to a particular time (for use in animations).
		'''
		# update the data, if we need to
		timestep = self._find_timestep(time)
		try:
			actual_time = self._gettimes()[timestep]
			timelabel = self._timestring(actual_time)
		except (ValueError, KeyError):
			actual_time = None
			timelabel = ''

		if timestep != self.currenttimestep:
			self.plotted['vline'].set_xdata(actual_time.jd - self.offset)
			self.plotted['text'].set_text(self._timestring(actual_time))
