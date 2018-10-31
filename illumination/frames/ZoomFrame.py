from .imshowFrame import *
from astropy.nddata.utils import Cutout2D


class ZoomFrame(imshowFrame):
    frametype = 'Zoom'

    def __init__(self,  source=None,
                        position=(0, 0),
                        size=(10, 10),
                        name='zoom',
                        cmapkw=dict(),
                        plotingredients=[   'image',
                                            'colorbar'], #'arrows','title'],
                        **kwargs):
        '''
        Initialize a ZoomFrame that can display
        images taken from a zoomed subset of
        a `source` imshowFrame. This is kind
        of like a magnifying class you can
        drop down on an image.

        Parameters
        ----------

        source : imshowFrame
                A frame into which this one will be zooming.

        position : (tuple)
                The (x, y) = (col, row) position of the center of zoom.

        shape : (tuple)
                The (x, y) = (ncols, nrows) shape of the zoom.

        name : str
            A name to give this Frame.

        ax : matplotlib.axes.Axes instance
            All plotting will happen inside this ax.
            If set to None, the `self.ax attribute` will
            need to be set manually before plotting.

        plotingredients : list
            A list of keywords indicating features that will be
            plotted in this frame. It can be modified either now
            when initializing the frame, or any time before
            calling `i.plot()` from the illustration.

        cmapkw : dict
            Dictionary of keywords to feed into the cmap generation.
        '''

        imshowFrame.__init__(self,  name=name, plotingredients=plotingredients, **kwargs)

        self.source = source
        self.position = position

        # cutout needs (row, col), but we want to give (x,y)
        self.size = size[::-1]

        # set the aspect ratio (width/height) for this zoom frame
        self.aspectratio = float(self.size[1])/self.size[0] #width/height

        self.titlefordisplay = '{} | {}'.format(self.frametype, self.position)

        self.cmapkw = copy.copy(cmapkw) # why do I have to do this?

    def _get_times(self):
        '''
        Get the available times associated with this frame.
        '''
        return self.source._get_times()

    def _find_timestep(self, time):
        '''
        Get the timestep, by using the source frame.
        '''
        return self.source._find_timestep(time)

    def _get_image(self, time=None):
        '''
        Get the image at a given time (defaulting to the first time),
        by pulling it from the source frame.
        '''

        bigimage, actual_time = self.source._get_image(time)
        self.cutout = Cutout2D(bigimage, self.position,
                               self.size, mode='partial')
        cutoutimage = self.cutout.data
        return cutoutimage, actual_time

    def plot(self, *args, **kwargs):

        # do all the normal stuff for an imshow plot
        imshowFrame.plot(self, *args, **kwargs)

        # add a box to the source image (cutout must have ben created, if plot has happened)
        self.cutout.plot_on_original(ax=self.source.ax, clip_on=True)

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
            self.plotted['image'].set_data(image)
            if 'time' in self.plotted:
                self.plotted['time'].set_text(self._timestring(actual_time))
        self.currenttimestep = timestep

    def __repr__(self):
        '''
        Default string representation for this frame.
        '''
        return '<{} Frame | position={} | size={}>'.format(self.frametype, self.position, self.size)
