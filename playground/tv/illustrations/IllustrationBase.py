from ...imports import *
from ..sequences import *
from ..frames import *
from ..colors import cmap_norm_ticks

def get_writer(filename, fps=30):
    '''
    Try to get an appropriate animation writer,
    given the filename provided.
    '''
    if '.mp4' in filename:
        try:
            writer = ani.writers['ffmpeg'](fps=fps)
        except (RuntimeError, KeyError):
            raise RuntimeError('This computer seems unable to ffmpeg.')
    else:
        try:
            writer = ani.writers['pillow'](fps=fps)
        except (RuntimeError, KeyError):
            writer = ani.writers['imagemagick'](fps=fps)
            raise RuntimeError('This computer seem unable to animate?')
    return writer

class IllustrationBase(Talker):
    '''
    This contains the basic layout and organization
    for a linked visualization of images.

    Other illustrations inherit from this basic one,
    changing the
    '''
    illustrationtype = 'Base'
    plotted = {}

    def __init__(self, nrows=1,
                       ncols=1,
                       figkw=dict(figsize=None, dpi=None),
                       sharecolorbar=True,
                       subplot_spec=None,
                       **gridspeckw):
        '''
        Initialize an Illustration,
        setting up its figure and basic layout.

        nrows : int
            The number of rows in the illustration.

        ncols : int
            The number of columns in the illustration.

        figkw : dict
            Keywords to pass along to create a figure.

        **gridspeckw : dict
            Any extra keywords are passed to the
            gridspec
        '''

        Talker.__init__(self, prefixformat='{:>32}')

        if subplot_spec is not None:
            # if there's a subplot_spec specified, then populate that
            self.figure = None

            subset = {k:gridspeckw.get(k) for k in ['wspace', 'hspace', 'height_ratios', 'width_ratios']}
            self.grid = gs.GridSpecFromSubplotSpec(nrows,
                                                    ncols,
                                                    subplot_spec=subplot_spec,
                                                    **subset)
            self.speak('built {} into an existing gridspec'.format(self.illustrationtype))
        else:
            # by default, create a new figure and grid spec
            self.figure = plt.figure(**figkw)
            self.grid = gs.GridSpec(nrows, ncols, **gridspeckw)
            self.speak('built {} into a new figure'.format(self.illustrationtype))


        # should this illustration have a shared colorbar, or separate ones?
        self.sharecolorbar = sharecolorbar

        # create an empty dictionary, where frames will be stored
        self.frames = {}

    def __repr__(self):
        '''
        How should this illustration be represented?
        '''
        return '<{} Illustration | ({} Frames)>'.format(self.illustrationtype, len(self.frames))

    def _get_times(self):
        '''
        Get *all* the times that are associated with this
        illustration, in any frame.
        '''

        # it's faster to convert from gps to floats and back again

        # make a list of gps times
        gps = [f._get_times().gps for f in self.frames.values()]

        # return that list, as times
        return Time(np.hstack(gps), format='gps', scale='tdb')

    def _timesandcadence(self, round=1):
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

                It is in units of seconds.
        '''

        try:
            self._precaculatedtimesandcadence
        except AttributeError:
            self._precaculatedtimesandcadence = {}
        try:
            times, cadence = self._precaculatedtimesandcadence[round]
        except KeyError:

            gps = np.hstack([f._get_times().gps for f in self.frames.values()])
            # alltimes =  Time(np.hstack(gps), format='gps')
            # alltimes = []
            # for k, f in self.frames.items():
            #	alltimes.extend(f._get_times())

            if round is None:
                diffs = np.diff(np.sort(gps))
                round = np.min(diffs[diffs > 0])

            baseline = np.min(gps)
            rounded = round * np.round((gps - baseline) / round) + baseline
            uniquegpstimes = np.unique(rounded)
            cadence = np.min(np.diff(uniquegpstimes)) * u.s
            # plt.figure('cadence!')
            # plt.plot(uniquegpstimes[:-1], np.diff(uniquegpstimes), '.')
            # plt.show()
            times = Time(uniquegpstimes, format='gps')
            self._precaculatedtimesandcadence[round] = times, cadence
        return times, cadence

    def plot(self, *args, **kwargs):
        '''
        Plot all the frames in this illustration.

        *args, **kwargs are passed to frames' .plot()
        '''
        for k, f in self.frames.items():
            f.plot(*args, **kwargs)

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
            # are the cmap, normalization, and ticks already defined?
            self.cmap, self.norm, self.ticks
        except AttributeError:

            # collect all the (first) images
            firstimages = []
            for name, frame in self.frames.items():
                try:
                    firstimages.extend(frame._get_image()[0].flatten())
                    self.speak('included {} in the shared color scheme'.format(frame))
                except (TypeError, IndexError, AttributeError):
                    self.speak('found no color scheme data for {}'.format(frame))

            # create the cmap from the given data
            self.cmap, self.norm, self.ticks = cmap_norm_ticks(
                np.asarray(firstimages), **kwargs)
            self.speak('defined color scheme with \n cmap={}\n norm={}\n ticks={}'.format(self.cmap,
                                                                                 self.norm,
                                                                                 self.ticks))
        return self.cmap, self.norm, self.ticks

    def _add_colorbar(self, imshowed, ax=None, ticks=None):
        '''
        Make a colorbar,
        attached to a particular axes
        (or multiple axes at once).

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
            # label=self.data.colorbarlabelfordisplay,
            fraction=0.04,
            pad=0.07,
            ticks=ticks)

        # colorbarred = plt.colorbar(self.plotted['image'], ax=axes, orientation='horizontal', label=self.data.colorbarlabelfordisplay, fraction=0.04, pad=0.07, ticks=ticks)
        colorbar.ax.set_xticklabels(
            ['{:.0f}'.format(v) for v in ticks], fontsize=8, color='gray')
        colorbar.outline.set_visible(False)

        return colorbar

    def savefig(self, filename, **savefigkw):
        '''
        Call plt.savefig, but make an announcement about it.
        This should be called after illustration.plot()

        Parameters
        ----------

        filename : str
            Where should the figure be saved?

        **savefigkw are passed to savefig
        '''

        plt.savefig(filename, **savefigkw)
        self.speak('saved figure to {}'.format(filename))


    def animate(self, filename='test.mp4',
                      mintime=None, maxtimespan=None, cadence=2 * u.s,
                      fps=30, dpi=None, **kw):
        '''
        Create an animation from an Illustration,
        using the time axes associated with each frame.

        This should be called after illustration.plot()

        Parameters
        ----------

        filename : str
        '''

        # figure out the times to display
        if mintime is None:
            actualtimes, actualcadence = self._timesandcadence(
                round=cadence.to('s').value)
            lower, upper = min(actualtimes.gps), max(
                actualtimes.gps) + actualcadence.to('s').value
        else:
            lower = mintime.gps
            upper = lower + maxtimespan.to('s').value

        if cadence is None:
            cadence = actualcadence.to('s').value
        else:
            # np.maximum(cadence.to('s').value, actualcadence.to('s').value)
            cadence = cadence.to('s').value

        if maxtimespan is not None:
            upper = lower + np.minimum(upper - lower, maxtimespan.to('s').value)

        times = np.arange(lower, upper, cadence)
        self.speak('about to animate {} times at {}s cadence for {}'.format(
            len(times), cadence, self))

        # get the writer
        writer = get_writer(filename, fps=fps)

        self.speak('the animation will be saved to {}'.format(filename))
        # set up the animation writer
        with writer.saving(self.figure,
                           filename,
                           dpi or self.figure.get_dpi()):

            for i, t in enumerate(times):
                self.speak('  {}/{} at {}'.format(i + 1,
                            len(times), Time.now().iso), progress=True)

                # update the illustration to a new time
                self.update(Time(t, format='gps', scale='tdb'))
                writer.grab_frame()
        self.speak('the animation is finished!')

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
