from .FrameBase import *
from ..sequences import make_image_sequence


class EmptyTimeseriesFrame(FrameBase):
    '''
    An EmptyTimeseriesFrame has a vertical bar for time when animated.

    The frame should be added to an illustration,
    the illustration should be plotted,
    and then data can be plotted into the
    ETF.ax and ETF.ax_hist frames.
    '''

    frametype = 'timeseries'

    def __init__(self, name='timeseries', xlim=[None, None], ylim=[None, None], ylabel='', histogram=True, **kwargs):
        '''
        Initialize an empty timeseries frame.

        Parameters
        ----------

        name : string
                A custom name for this frame.

        xlim : tuple
                Set the xlimits. If None, wait for data to appear.

        ylim : tuple
                Set the ylimits. If None, wait for data to appear.

        ylabel : string
                Set a ylabel for this plot.

        histogram : bool
                Should we add an extra axis for a histogram?
        '''
        # initialize an empty frame
        FrameBase.__init__(self, name=name, **kwargs)

        # store the plot limits
        self.xmin, self.xmax = xlim
        self.ymin, self.ymax = ylim

        # store the custom title for this one
        self.titlefordisplay = ylabel

        # should this frame have a histrogram attached to it?
        self.histogram = histogram

    def plot(self, t=None, y=None, **kwargs):
        '''
        Make an empty plot, with a vertical line waiting in it.
        '''

        self.plotted = {}

        if t is not None:
            self.plotted['data'] = self.ax.plot(t-self.offset, y, **kwargs)

        if self.histogram:
            b = self.ax.get_position()
            width = b.x1 - b.x0
            scale = 0.1
            self.ax_hist = self.ax.figure.add_axes(
                [b.x1, b.y0, b.width * scale, b.height])
            self.ax_hist.set_facecolor('lightgray')
            self.ax_hist.set_axis_off()
            self.ax.set_position([b.x0, b.y0, b.width, b.height])

        # plot the time bar
        self.plotted['vline'] = self.ax.axvline(
            np.nan, color='gray', alpha=0.5, zorder=-1e6)

        # pull the title for this frame
        self.ax.set_ylabel(self.titlefordisplay)
        if self.ax.get_xticklabels()[0].get_visible():
            self.ax.set_xlabel('Time - {:.5f} (days)'.format(self.offset))

        # turn the axes lines off
        # plt.axis('off')

        # keep track of the current plotted timestep
        self.currenttimestep = None

        # only set the limits if we need to; otherwise, let the first plot do it
        if self.xmin is not None and self.xmax is not None:
            plt.xlim(self.xmin, self.xmax)
        if self.ymin is not None and self.ymax is not None:
            plt.ylim(self.ymin, self.ymax)

    def update(self, time):
        '''
        Update this frame to a particular time (for use in animations).
        '''

        # add a vertical line
        v = time.jd - self.offset
        self.plotted['vline'].set_xdata(v)
        #self.speak('offset is {}'.format(self.offset))
        #self.speak('drew vertical line at {}'.format(v))
        # add a time label
        #s = self._timestring(time)
        # try:
        #	self.plotted['time'].set_text(s)
        # except KeyError:
        #	self.plotted['time'] = self.ax.text(0.01, +0.02, s, va='bottom', zorder=1e6, transform=self.ax.transAxes)

        self.currenttimestep = time
