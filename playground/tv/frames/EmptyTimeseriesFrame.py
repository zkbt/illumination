from .FrameBase import *
from ..sequence import make_sequence

class EmptyTimeseriesFrame(FrameBase):
	'''
	An EmptyTimeseriesFrame has a vertical bar
	indicating the time, which can move when animated.

	Other data can be plotted into the axes,
	after the illustration has been plotted once.

	'''

	frametype = 'timeseries'
	def __init__(self, xlim=[None, None], ylim=[None, None], title='', histogram=True, name='timeseries', **kwargs):

		# initialize an empty frame
		FrameBase.__init__(self, name=name, **kwargs)

		# store the plot limits
		self.xmin, self.xmax = xlim
		self.ymin, self.ymax = ylim

		# store the custom title for this one
		self.titlefordisplay =  title

		# should this frame have a histrogram attached to it?
		self.histogram = histogram

	def plot(self,  **kwargs):
		'''
		Add a vertical line, and set the limits.
		'''

		self.plotted = {}

		# make sure we point back at this frame
		plt.sca(self.ax)

		if self.histogram:
			b = self.ax.get_position()
			#self.ax_hist = self.ax.figure.add_axes([b.x0, b.y0, b.x1, b.y1])

		# plot the time bar


		# pull the title for this frame
		plt.ylabel(self.titlefordisplay)
		if self.ax.get_xticklabels()[0].get_visible():
			plt.xlabel('Time - {:.5f} (days)'.format(self.offset))

		# turn the axes lines off
		# plt.axis('off')

		# keep track of the current plotted timestep
		self.currenttimestep = None

		# only set the limits if we need to; otherwise, let the first plot do it
		if self.xmin is not None and self.xmax is not None:
			plt.xlim(self.xmin, self.xmax)
		if self.ymin is not None and self.ymax is not None:
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

		# add a vertical line
		v = time.jd - self.offset
		try:
			self.plotted['vline'].set_xdata(v)
		except KeyError:
			self.plotted['vline'] = self.ax.axvline(v, color='gray', alpha=0.5, zorder=-1e6)

		# add a time label
		#s = self._timestring(time)
		#try:
		#	self.plotted['text'].set_text(s)
		#except KeyError:
		#	self.plotted['text'] = self.ax.text(0.01, +0.02, s, va='bottom', zorder=1e6, transform=self.ax.transAxes)

		self.currenttimestep = time
