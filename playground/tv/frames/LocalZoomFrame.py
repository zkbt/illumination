from .ZoomFrame import *
from astropy.nddata.utils import Cutout2D
from matplotlib.patches import Rectangle


class LocalZoomFrame(ZoomFrame):
    frametype = 'Zoom'

    def __init__(self, source, position=(0, 0), size=(10, 10), zoom=10, **kwargs):
        '''
        Initialize a ZoomFrame that can display
        images taken from a zoomed subset of
        a `source` imshowFrame. This is kind
        of like a magnifying class you can
        drop down on an image.

        It *doesn't* add a new axis.

        Parameters
        ----------

        source : imshowFrame
                A frame into which this one will be zooming.

        position : (tuple)
                The (x, y) = (col, row) position of the center of zoom.
                (These are in original image coordinates,
                not those that have been transformed for display.)

        shape : (tuple)
                The (x, y) = (ncols, nrows) shape of the zoom.
        '''

        ZoomFrame.__init__(self,  **kwargs)

        #
        self.source = source
        self.source.includes.append(self)

        self.position = position
        self.size = size
        self.zoom = zoom

        self.titlefordisplay = '{} | {}'.format(self.frametype, self.position)

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

        # get the image, transform to the rotated camera frame
        transformedbigimage, actual_time = self.source._get_image(time)

        # get the position of this stamp, transformed to the rotated camera frame
        transformedxy = self.source._transformxy(*self.position)
        self.cutout = Cutout2D(transformedbigimage,
                               transformedxy, self.size, mode='partial')

        # all coordinates for the cutout are now in the transformed coordinates
        cutoutimage = self.cutout.data
        return cutoutimage, actual_time

    def plot(self, time=None):
        '''
        Generate the (initial) plot for this local zoom frame.

        Individual features can be modified afterwards,
        through the .ax (the plotted axes) or the .plotted
        (dictionary of plotted elements) attributes.

        Parameters
        ----------

        time : astropy Time
            The time to plot, defaults to the first with None.
        '''

        # pull out the array to work on
        image, actual_time = self._get_image(time)

        # extract the cmap from the source image
        cmap, norm, ticks = self.source._cmap_norm_ticks(image)


        # these are in the rotated camera frame
        x, y = self.cutout.center_original
        ysize, xsize = self.cutout.shape

        left, right = x - xsize * self.zoom / 2, x + xsize * self.zoom / 2
        bottom, top = y - ysize * self.zoom / 2, y + ysize * self.zoom / 2

        extent = [left, right, bottom, top]

        zooms = [self.illustration.frames[k]
                 for k in self.illustration.frames.keys() if 'zoom' in k]
        zorder = zooms.index(self)

        self.plotted['image'] = self.source.ax.imshow(image,
                                                     extent=extent,
                                                     interpolation='nearest',
                                                     origin='lower',
                                                     norm=norm, cmap=cmap,
                                                     zorder=zorder)

        # reate a Rectangle patch
        rect = Rectangle((left, bottom), xsize * self.zoom, ysize * self.zoom,
                         linewidth=1, edgecolor='black', facecolor='none',
                         zorder=zorder + 0.5, clip_on=True)

        # Add the patch to the Axes
        self.plotted['boxonzoom'] = self.source.ax.add_patch(rect)

        self.source.ax.set_clip_on(True)
        # add a box to the source image (cutout must have ben created, if plot has happened)
        #boxonoriginal = self.cutout.plot_on_original(ax=self.source.ax, clip_on=True)

        try:
            timestep = self._find_timestep(time)
        except:
            timestep = None
        self.currenttimestep = timestep

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
                timestring = self.source._timestring(actual_time)
                self.source.plotted['time'].set_text(timestring)
        self.currenttimestep = timestep
