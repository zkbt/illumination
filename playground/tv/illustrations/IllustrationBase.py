from ...imports import *
from ..frames import *
from ..colors import cmap_norm_ticks

class IllustrationBase:
	'''
	This contains the basic layout and organization
	for a linked visualization of images.
	'''
	illustrationtype = 'Base'
	def __init__(self, nrows=1, ncols=1, figkw=dict(figsize=None, dpi=None), sharecolorbar=True, **kwargs):
		'''
		Initialize an Illustration,
		setting up its figure and basic layout.
		'''
		self.figure = plt.figure(**figkw)
		self.grid = gs.GridSpec(nrows, ncols, **kwargs)
		self.sharecolorbar = sharecolorbar
		self.frames = {}

	def __repr__(self):
		return '<{} Illustration | ({} Frames) >'.format(self.illustrationtype, len(self.frames))

	def _gettimes(self):
		alltimes = []
		for k, f in self.frames.items():
			alltimes.extend(f._gettimes())
		return alltimes

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


		alltimes = []
		for k, f in self.frames.items():
			alltimes.extend(f._gettimes())

		if round is None:
			diffs = np.diff(np.sort(alltimes))
			round = np.min(diffs[diffs > 0])

		baseline = np.min(alltimes)
		rounded = round*np.round(np.array(alltimes-baseline)/round) + baseline
		times = np.unique(rounded)
		cadence = np.min(np.diff(times))
		return times, cadence




	def plot(self, *args, **kwargs):
		'''
		Plot all the frames in this illustration.

		*args, **kwargs are passed to frames' .plot()
		'''
		for k, f in self.frames.items():
			f.plot(*args, **kwargs)
			print('plotting {}'.format(k))

	def update(self, *args, **kwargs):
		'''
		Update all the frames in this illustration.

		*args, **kwargs are passed to the frames' .update()
		'''
		for k, f in self.frames.items():
			f.update(*args, **kwargs)


	def _cmap_norm_ticks(self, **kwargs):
		'''
		Return the cmap and normalization.

		Make a colorbar for this illustration,
		using the first image from every frame.

		**kwargs are passed to colors.cmap_norm_ticks
		'''

		try:
			self.cmap, self.norm, self.ticks
		except AttributeError:
			firstimages = []
			for name, frame in self.frames.items():
				try:
					firstimages.extend(frame.data[0].flatten())
					print('including {} in shared colorbar'.format(frame))
				except (TypeError,IndexError):
					print('found no data for {}'.format(frame))
			# create the cmap from the given data
			self.cmap, self.norm, self.ticks = cmap_norm_ticks(np.asarray(firstimages), **kwargs)
		return self.cmap, self.norm, self.ticks

	def _add_colorbar(self, imshowed, ax=None, ticks=None):

		'''
		Make a colorbar,
		attached to a particular axes.

		Parameters
		----------
		imshowed : the output of plt.imshow
			the colorbar will be extracted from this imshow
		ax : axes object
			this colorbar will be attached to this axes

		'''


		if ax is None:
			ax = [f.ax for f in self.frames.values() if f.ax is not None]

		# make a colorbar attached to the frame
		#	axes =
		colorbar = plt.colorbar(
							imshowed,
							ax=ax,
							orientation='horizontal',
							#label=self.data.colorbarlabelfordisplay,
							fraction=0.04,
							pad=0.07,
							ticks=ticks)

		#colorbarred = plt.colorbar(self.plotted['imshow'], ax=axes, orientation='horizontal', label=self.data.colorbarlabelfordisplay, fraction=0.04, pad=0.07, ticks=ticks)
		colorbar.ax.set_xticklabels(['{:.0f}'.format(v) for v in ticks])
		colorbar.outline.set_visible(False)

		return colorbar
"""
class Row(IllustrationBase):
	'''
	FIXME -- the initialization is probably still sketchy on this.
	'''

	def __init__(self, *frameargs, **framekwargs):

		# store all the frames in a dictionary
		self.frames = {}
		for i, a in enumerate(frameargs):
			self.frames[i] = a

		for i, k in enumerate(framekwargs.keys()):
			self.frames[k] = framekwargs[k]

		# set up the geometry of the figure
		self.orientation = 'horizontal'
		cols = len(self.frames)
		rows = 1
		IllustrationBase.__init__(self, rows, cols,
								hspace=0.02, wspace=0.02,
								left=0.05, right=0.95,
								bottom=0.1, top=0.9)

		# initiate the axes for each camera
		keys = list(range(len(frameargs))) + list(framekwargs.keys())
		for j, k in enumerate(keys):

			# populate the axes on the main camera grid
			ax = plt.subplot(self.grid[0, j])
			self.frames[k].ax = ax
"""
