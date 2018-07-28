from .FrameBase import *
from ..colors import cmap_norm_ticks
from ..sequences import make_sequence


class imshowFrame(FrameBase):
    '''
    An imshow frame can show a sequence of images, as an imshow.
    '''

    frametype = 'imshow'
    xmin, xmax = None, None
    ymin, ymax = None, None

    def __init__(self, ax=None, data=None, name='image', title=None, cmapkw={}, **kwargs):
        FrameBase.__init__(self, ax=ax, data=data, name=name,  **kwargs)

        # ensure that the data are a sequence of images
        self.data = make_sequence(self.data, **kwargs)

        # if there's an image, use it to set the size
        try:
            self.xmin, self.ymin = 0, 0
            self.ymax, self.xmax = self.data[0].shape
        except (IndexError, AttributeError, TypeError):
            pass

        try:
            self.titlefordisplay = self.data.titlefordisplay
        except AttributeError:
            self.titlefordisplay = ''
        if title is not None:
            self.titlefordisplay = title

        self.cmapkw = cmapkw

    def _cmap_norm_ticks(self, *args, **kwargs):
        '''
        Return the cmap and normalization.

        If the illustration has shared colorbar,
        then use the cmap and norm from there.

        Otherwise, make a colorbar for this frame.

        *args and **kwargs are passed to colors.cmap_norm_ticks
        '''

        if self.illustration.sharecolorbar:
            # pull the cmap and normalization from the illustration
            self.cmap, self.norm, self.ticks = self.illustration._cmap_norm_ticks(**kwargs)
            return self.cmap, self.norm, self.ticks
        else:
            try:
                return self.cmap, self.norm, self.ticks
            except AttributeError:
                # create the cmap from the given data
                self.cmap, self.norm, self.ticks = cmap_norm_ticks(
                    *args, **kwargs)

                return self.cmap, self.norm, self.ticks

    def _ensure_colorbar_exists(self, image):
        '''
        Make sure this axes has its colorbar created.

        Parameters
        ----------

        image : the output from imshow

        '''
        if self.illustration.sharecolorbar:
            # try to use a shared colorbar for the whole illustration
            try:
                self.illustration.colorbar
            except AttributeError:
                self.illustration.colorbar = self.illustration._add_colorbar(
                    image, ticks=self.ticks)
        else:
            try:
                self.colorbar
            except:
                # create a colorbar for this illustration
                self.colorbar = self.illustration._add_colorbar(
                    image, self.ax, ticks=self.ticks)

    def draw_arrows(self, origin=(0, 0), ratio=0.05):
        '''
        Draw arrows on this Frame, to indicate
        the +x and +y directions.
        '''

        try:
            xspan = np.abs(self.xmax - self.xmin)
            yspan = np.abs(self.ymax - self.ymin)
            length = ratio * np.maximum(xspan, yspan)
        except:
            length = 50

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

        # pull out the array to work on
        image, actual_time = self._get_image()
        if actual_time is None:
            timelabel = ''
        else:
            # pull out the cmap, normalization, and suggested ticks
            cmap, norm, ticks = self._cmap_norm_ticks(image, **self.cmapkw)

            # display the image for this frame
            extent = [0, image.shape[1], 0, image.shape[0]]

            # make a stacked image
            try:
                assert(np.size(image) < 10000 or self.data.N < 50)
                firstimage = self.data.median()
            except (AttributeError, AssertionError):
                firstimage = image
            self.plotted['imshow'] = self.ax.imshow(
                firstimage, extent=extent, interpolation='nearest', origin='lower', norm=norm, cmap=cmap)

            # define the timelabel
            timelabel = self._timestring(self._gettimes()[timestep])

            # add the colorbar
            self._ensure_colorbar_exists(self.plotted['imshow'])

        # add a time label
        self.plotted['text'] = self.ax.text(
            0.0, -0.02, timelabel, va='top', zorder=1e6, color='gray', transform=self.ax.transAxes)

        # pull the title for this frame
        plt.title(self.titlefordisplay)

        # turn the axes lines off
        plt.axis('off')

        # keep track of the current plotted timestep
        self.currenttimestep = timestep

        plt.xlim(self.xmin, self.xmax)
        plt.ylim(self.ymin, self.ymax)

        self.plotted['arrow'] = self.draw_arrows()
        # self.ax.set_facecolor('black')

    """
	def _timestring(self, time):
		'''
		Return a string, given an input time (still in spacecraft time).
		'''
		try:
			offset = np.min(self.illustration._gettimes())
		except AttributeError:
			print('no illustration times found!')
			offset=0

		return 't={:.5f}{:+.5f}'.format(offset.jd, (time-offset).to('day'))
	"""

    def _get_image(self, time=None):
        '''
        Get the image at a given time (defaulting to the first time).
        '''

        try:
            if time is None:
                time = self._gettimes()[0]
            timestep = self._find_timestep(time)
            rawimage = self.data[timestep]
            assert(rawimage is not None)
            image = self._transformimage(rawimage)
            actual_time = self._gettimes()[timestep]
            #print(" ")
            #print(time, timestep)
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
                actual_time = self._gettimes()[timestep]
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
            self.plotted['imshow'].set_data(image)

            self.plotted['text'].set_text(self._timestring(actual_time))
