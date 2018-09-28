from ..imports import *


class FrameBase(Talker):

    frametype = 'base'
    timeunit = 'day'
    aspectratio = 1

    def __init__(self,
                    name='',
                    ax=None,
                    data=None,
                    illustration=None,
                    plotingredients=[],
                    **kwargs):
        '''
        Initialize this Frame, which can be one (of multiple)
        frames in an Illustration. Before plotting, each frame
        needs to have an `ax` defined saying where it should be
        plotted and (generally) some `data` associated with it.

        Parameters
        ----------

        name : str
            A name to give this Frame.

        ax : matplotlib.axes.Axes instance
            All plotting will happen inside this ax.
            If set to None, the `self.ax attribute` will
            need to be set manually before plotting.

        data : flexible
            It can be custom object (e.g. a Stamp),
            or simple arrays, or a list of HDULists,
            or something else, depending on
            what this actual Frame does with it
            in `plot` and `update`.

        illustration : an Illustration
            The illustration in which this frame will be embedded.
            We keep track of this (sometimes) because we might want
            information that's shared across the whole illustration
            to be accessible to this individual frame when plotting.

        plotingredients : list
            A list of keywords indicating features that will be
            plotted in this frame. It can be modified either now
            when initializing the frame, or any time before
            calling `i.plot()` from the illustration.

        **kwargs go nowhere (?)
        '''

        # initialize the Talker
        Talker.__init__(self, prefixformat='{:>32}')

        # store a name for this frame
        self.name = name

        # assign this frame an axes to sit in
        self.ax = ax

        # this is likely a Sequence of some kind
        self.data = data

        # is there another overarching frame this one should be aware of?
        self.illustration = illustration

        # what ingredients should be included when plotting?
        self.plotingredients = list(plotingredients)

        # keep track of a list of frames included in this one (e.g. zooms)
        self.includes = []

        # keep track of what's been plotted
        self.plotted = {}


    @property
    def offset(self):
        '''
        Get a time offset, to use as a zero-point.

        Returns
        -------
        offset : float
                An appropriate time zero-point (in JD).
        '''

        # is an offset already defined?
        try:
            return self._offset
        except AttributeError:
            # is there a minimum of the illustration's times?
            try:
                self._offset = np.min(self.illustration._get_times().jd)
            except (AttributeError, ValueError):
                # otherwise, use only this frame to estimate the offset
                try:
                    self._offset = np.min(self._get_times().jd)
                except ValueError:
                    self._offset = 0.0
            self.speak('defining {} as the time offset'.format(self._offset))

            return self._offset

    def _timestring(self, time):
        '''
        Return a string, given an input time.

        Parameters
        ----------
        time : astropy Time
                A particular time.

        Returns
        -------
        timestring : str
                A string describing the times.
        '''

        if self.data._timeisfake:
            timestep = self._find_timestep(time)
            return '#{:.0f}'.format(self._get_times()[timestep].gps)
        else:
            days = time.jd - self.offset
            inunits = (days * u.day).to(self.timeunit)
            return 't={:.5f}{:+.5f}'.format(self.offset, inunits)

    def __repr__(self):
        '''
        Default string representation for this frame.
        '''
        return '<{} Frame | data={} | name={}>'.format(self.frametype,
                                                       self.data,
                                                       self.name)
    def __str__(self):
        return '<F"{}">'.format(self.name)

    def plot(self):
        '''
        This should be redefined in a class that inherits from FrameBase.
        '''
        raise RuntimeError(
            "Don't know how to `plot` {}".format(self.frametype))

    def update(self, *args, **kwargs):
        '''
        This should be redefined in a class that inherits from FrameBase.
        '''
        raise RuntimeError(
            "Don't know how to `update` {}".format(self.frametype))

    def _find_timestep(self, time):
        '''
        Given a time, identify its index.

        Parameters
        ----------

        time : float
                A single time (in JD?).

        Returns
        -------
        index : int
                The index of the *closest* time point.
        '''
        return self.data._find_timestep(time)

    def _get_times(self):
        '''
        Get the available times associated with this frame.
        '''

        # does the data have a time axis defined?
        try:
            return self.data.time
        # if not, return an empty time
        except AttributeError:
            return Time([], format='gps')

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
            gps = self._get_times().gps

            if round is None:
                diffs = np.diff(np.sort(gps))
                round = np.min(diffs[diffs > 0])

            baseline = np.min(gps)
            rounded = round * np.round((gps - baseline) / round) + baseline
            uniquegpstimes = np.unique(rounded)
            cadence = np.min(np.diff(uniquegpstimes)) * u.s
            times = Time(uniquegpstimes, format='gps')
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
            return 'horizontal' #'vertical'
