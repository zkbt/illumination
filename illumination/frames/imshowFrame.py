from .FrameBase import *
from ..colors import cmap_norm_ticks
from ..sequences import make_image_sequence


class imshowFrame(FrameBase):
    '''
    An imshow frame can show a sequence of images, as an imshow.
    '''

    # what is the type of this frame?
    frametype = 'imshow'

    # what are the coordinate limits?
    xmin, xmax = None, None
    ymin, ymax = None, None

    def __init__(self,
                 name='image',
                 ax=None,
                 data=None,
                 title=None,
                 plotingredients=[  'image',
                                    'time',
                                    'colorbar',
                                    'arrows',
                                    'title'], # other options might be 'filename', 'axes', what else?
                 processingsteps=[],
                 firstframe=None,
                 cmapkw=dict(),
                 **kwargs):
        '''
        Initialize this imshowFrame, will can show a sequence of 2D images.

        Parameters
        ----------

        name : str
            A name to give this Frame.

        ax : matplotlib.axes.Axes instance
            All plotting will happen inside this ax.
            If set to None, the `self.ax attribute` will
            need to be set manually before plotting.

        data : Image_Sequence
            Any Sequence that contains 2D images.

        title : str
            A string to display as the title of this frame.
            If nothing, this will try to pull a title out
            of the data, or leave it blank.

        plotingredients : list
            A list of keywords indicating features that will be
            plotted in this frame. It can be modified either now
            when initializing the frame, or any time before
            calling `i.plot()` from the illustration.

        cmapkw : dict
            Dictionary of keywords to feed into the cmap generation.
        '''

        # initialize the frame base
        FrameBase.__init__(self, name=name,
                                 ax=ax,
                                 data=data,
                                 plotingredients=plotingredients,
                                 **kwargs)

        # ensure that the data are a sequence of images
        self.data = make_image_sequence(self.data, **kwargs)

        # if there's an image, use it to set the size
        try:
            self.xmin, self.ymin = 0, 0
            self.ymax, self.xmax = self.data[0].shape
        except (IndexError, AttributeError, TypeError):
            pass

        # try to figure out a title for the imshowFrame
        try:
            self.titlefordisplay = self.data.titlefordisplay
        except AttributeError:
            self.titlefordisplay = ''

        if title is not None:
            self.titlefordisplay = title

        # keep track of an extra keywords for generating the cmaps
        self.cmapkw = copy.copy(cmapkw) # why do I have to do this?

        # are there steps to apply to the image before displaying?
        self.processingsteps = processingsteps

        # should we plot something special for the first frame?
        self.firstframe = firstframe

    def _cmap_norm_ticks(self, *args, **cmapkw):
        '''
        Return the cmap and normalization.

        If the illustration has shared colorbar,
        then use the cmap and norm from there.

        Otherwise, make a colorbar for this frame.

        *args and **kwargs are passed to colors.cmap_norm_ticks
        '''

        if self.illustration.sharecolorbar:
            # pull the cmap and normalization from the illustration
            (self.plotted['cmap'],
             self.plotted['norm'],
             self.plotted['ticks']) = self.illustration._cmap_norm_ticks(**self.illustration.cmapkw)
            return (self.plotted['cmap'],
                    self.plotted['norm'],
                    self.plotted['ticks'])
        else:
            # use already-defined properties, or make new ones
            try:
                return  (self.plotted['cmap'],
                         self.plotted['norm'],
                         self.plotted['ticks'])
            except KeyError:

                # create the cmap from the given data
                (self.plotted['cmap'],
                 self.plotted['norm'],
                 self.plotted['ticks']) = cmap_norm_ticks(*args, **cmapkw)

                return  (self.plotted['cmap'],
                         self.plotted['norm'],
                         self.plotted['ticks'])

    def _ensure_colorbar_exists(self, image):
        '''
        Make sure this axes has its colorbar created.

        Parameters
        ----------

        image : the output returned from imshow

        '''
        # do we use a shared colorbar for the whole illustration?
        if self.illustration.sharecolorbar:
            self.speak('making sure a shared colorbar is set up for {}'.format(self))
            try:
                # if the illustration already has a colorbar, don't remake
                self.illustration.plotted['colorbar']
            except KeyError:
                # if the illustration needs a colorbar, make one!
                self.speak('added a shared colorbar for {}'.format(self.illustration))

                c = self.illustration._add_colorbar(image,
                                                    ax=None,
                                                    ticks=self.plotted['ticks'])
                self.illustration.plotted['colorbar'] = c
            return self.illustration.plotted['colorbar']
        # or do we just give this one frame its own colorbar?
        else:
            self.speak('making sure a unique colorbar is set up for {}'.format(self))
            try:

                self.plotted['colorbar']
            except KeyError:
                self.speak('added a unique colorbar for {}'.format(self))


                # create a colorbar for this illustration
                c = self.illustration._add_colorbar(image,
                                                    ax=self.ax,
                                                    ticks=self.plotted['ticks'])
                self.plotted['colorbar'] = c
            return self.plotted['colorbar']


    def draw_arrows(self, origin=(0, 0), ratio=0.05):
        '''
        Draw arrows on this Frame, to indicate
        the +x and +y directions.

        Parameters
        ----------
        origin : tuple
            The (x,y) coordinates of the corner of the arrows.
        ratio : float
            What fraction of the (longest) axis should the arrows span?
        '''


        # figure out the length of the arrows (in data units)
        try:
            xspan = np.abs(self.xmax - self.xmin)
            yspan = np.abs(self.ymax - self.ymin)
            length = ratio * np.maximum(xspan, yspan)
        except:
            length = 50

        # store the arrows in a dictionary
        arrows = {}

        # rotate into the display coordinates
        unrotatedx, unrotatedy = origin
        x, y = self._transformxy(*origin)
        arrow_kw = dict(zorder=10, color='black', width=length * 0.03, head_width=length *
                        0.3, head_length=length * 0.2, clip_on=False, length_includes_head=True)
        text_kw = dict(va='center', color='black', ha='center',
                       fontsize=7, fontweight='bold', clip_on=False)
        buffer = 1.4

        # +x arrow
        dx, dy = np.asarray(self._transformxy(unrotatedx + length, unrotatedy)) - \
            np.asarray(self._transformxy(unrotatedx, unrotatedy))
        arrows['xarrow'] = self.ax.arrow(x, y, dx, dy, **arrow_kw)
        xtextx, xtexty = self._transformxy(
            unrotatedx + length * buffer, unrotatedy)
        arrows['xarrowlabel'] = self.ax.text(xtextx, xtexty, 'x', **text_kw)

        # +y arrow
        dx, dy = np.asarray(self._transformxy(unrotatedx, unrotatedy + length)) - \
            np.asarray(self._transformxy(unrotatedx, unrotatedy))
        arrows['yarrow'] = self.ax.arrow(x, y, dx, dy, **arrow_kw)
        ytextx, ytexty = self._transformxy(
            unrotatedx, unrotatedy + length * buffer)
        arrows['yarrowlabel'] = self.ax.text(ytextx, ytexty, 'y', **text_kw)

        return arrows

    def plot(self, time=None):
        '''
        Generate the (initial) plot for this frame.

        Individual features can be modified afterwards,
        through the .ax (the plotted axes) or the .plotted
        (dictionary of plotted elements) attributes.

        Parameters
        ----------

        time : astropy Time
            The time to plot, defaults to the first with None.
        '''

        self.speak('plotting {} for the first time'.format(self))

        # make sure we point back at this frame
        plt.sca(self.ax)

        # kind of a kludge (to make the plots and cmaps reset)?
        self.plotted = {}

        # pull out the array to work on
        image, actual_time = self._get_image(time)

        # plot the image, as an imshow
        if ('image' in self.plotingredients):# and (image is not None):

            # pull out the cmap, normalization, and suggested ticks

            cmap, norm, ticks = self._cmap_norm_ticks(image, **self.cmapkw)

            # display the image for this frame
            extent = [0, image.shape[1], 0, image.shape[0]]

            # make a stacked image
            if self.firstframe is None:
                firstimage = image
            elif self.firstframe == 'median':
                #assert(np.size(image) < 10000 or self.data.N < 50)
                firstimage = self.data.median()

            self.plotted['image'] = self.ax.imshow(
                firstimage, extent=extent, interpolation='nearest', origin='lower', norm=norm, cmap=cmap)

            self.speak('added image of shape {} to {}'.format(firstimage.shape, self))

        # plot the colorbar
        if ('colorbar' in self.plotingredients) and 'image' in self.plotted:
            # add the colorbar
            self.plotted['colorbar'] = self._ensure_colorbar_exists(self.plotted['image'])

        # plot some text labeling the time
        if 'time' in self.plotingredients:
            if actual_time is None:
                timelabel = ''
            else:
                timelabel = self._timestring(actual_time)

            # add a time label
            self.plotted['time'] = self.ax.text(
                0.0, -0.02, timelabel, va='top', zorder=1e6, color='gray', transform=self.ax.transAxes)
            self.speak('added time label of "{}" on {}'.format(timelabel, self))

        # plot the arrows
        if 'arrows' in self.plotingredients:
            self.plotted['arrows'] = self.draw_arrows()
            self.speak('added arrows on {}'.format(self))

        # plot a title on this frame
        if 'title' in self.plotingredients:
            self.plotted['title'] = plt.title(self.titlefordisplay)
            self.speak('added title of "{}" to {}'.format(self.titlefordisplay, self))

        # plot lines and ticks for axes only if requested
        if 'axes' not in self.plotingredients:
            # turn the axes lines off
            plt.axis('off')

        # change the x and y limits, if need be
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_aspect('equal')

        # keep track of the current plotted timestep
        try:
            timestep = self._find_timestep(time)
        except:
            timestep = None
        self.currenttimestep = timestep

    def process_image(self, image):
        '''
        Apply any extra processing steps to the image
        (subract a median image, normalize, mask, ???)
        '''

        if 'subtractmedian' in self.processingsteps:
            processedimage = image - self.data.median()
            #self.speak('subtracted median image')
        elif 'subtractmean' in self.processingsteps:
            processedimage = image - self.data.mean()
        else:
            processedimage = image
        return processedimage

    def _get_image(self, time=None):
        '''
        Get the image at a given time (defaulting to the first time).
        '''

        try:
            if time is None:
                time = self._get_times()[0]
            timestep = self._find_timestep(time)
            rawimage = self.data[timestep]
            assert(rawimage is not None)

            processedimage = self.process_image(rawimage)
            image = self._transformimage(processedimage)
            actual_time = self._get_times()[timestep]
            # self.speak(" ")
            # self.speak(time, timestep)
        except (IndexError, AssertionError, ValueError):
            return None, None
        return image, actual_time

    def _get_alternate_time(self, time=None):
        '''
        The time are still a little kludgy.
        (Maybe this isn't even necessary?)
        '''
        for f in self.includes:
            try:
                timestep = f._find_timestep(time)
                actual_time = self._get_times()[timestep]
                break
            except IndexError:
                pass
        return actual_time

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
            if 'image' in self.plotingredients:
                self.plotted['image'].set_data(image)
            if 'time' in self.plotingredients:
                self.plotted['time'].set_text(self._timestring(actual_time))
        self.currenttimestep = timestep
