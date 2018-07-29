from .IllustrationBase import *

__all__ = ['HybridIllustration']


class HybridIllustration(IllustrationBase):
    illustrationtype = 'Timeseries'

    def __init__(self,  imshows=[],
                        timeseries=[],
                        imshowheight=0.5,
                        sizescale=3,
                        figsize=None,
                        **illkw):
        '''
        Initialize an illustration from list of frames.

        Parameters
        ----------

        imshows : list
            A list of imshow frames, to be displayed in a row on the top.

        timeseries : list
            A list of timeseries frames, to be displayed in rows below.

        imshowheight : float
            How tall is the imshow, compared to the entire timeseries block?

        sizescale : float
            An overall size scale, in inches.

        figsize : tuple
            Override the automated figure size with your own, in inches.

        **illkw keywords are passed to IllustrationBase
        '''


        # one row for imshows + one for each timeseries
        hasimshow = int(len(imshows) > 0)
        rows = hasimshow + len(timeseries) + 1

        # one column for each imshow
        cols = np.maximum(1, len(imshows))

        # use the frame aspect ratios to set the width ratios
        width_ratios = [f.aspectratio for f in imshows]

        # set the height ratios, including a gap between imshows and timeseries
        height_ratios = hasimshow * [imshowheight]
        if len(timeseries) > 0:
            height_ratios = (height_ratios +
                             [0.5 / len(timeseries)] +
                             len(timeseries) * [1.0 / len(timeseries)])


        # set the basic layout
        hspace, wspace = 0.15, 0.08
        left, right = 0.1, 0.9
        bottom, top = 0.1, 0.9

        # set the sizes, trying to keep square imshows square
        wsize = sizescale * cols * (1 + (cols - 1) * wspace) / (right - left)
        hsize = sizescale * np.sum(height_ratios) * \
            (1 + (rows - 1) * hspace) / (top - bottom)

        # allow the user to overwrite the automatic figure size
        figkw = dict(figsize=(figsize or (wsize, hsize)))

        # create a illustration to match this geometry
        IllustrationBase.__init__(self, rows, cols,
                                  figkw=figkw,
                                  hspace=hspace, wspace=wspace,
                                  left=left, right=right,
                                  bottom=bottom, top=top,
                                  height_ratios=height_ratios,
                                  width_ratios=width_ratios,
                                  **kwargs)

        # add the imshows
        for col, i in enumerate(imshows):
            row = 0

            # make sure to connect the frame back to this illustration
            i.illustration = self
            # create the axes in which this should sit
            i.ax = plt.subplot(self.grid[row, col])

            # register this in the frames dictionary
            try:
                n = i.name
                if n in self.frames:
                    n += '-{}'.format(col)
            except AttributeError:
                n = (row, col)
            self.frames[n] = i

        # add the timeseries
        sharex = None  # you may want to change the shared axes for different visualizations
        for row, t in enumerate(timeseries):
            col = 0

            # make sure to connect the frame back to this illustration
            t.illustration = self
            # create the axes in which this should sit
            t.ax = plt.subplot(
                self.grid[row + hasimshow + 1, :], sharex=sharex)
            sharex = t.ax

            # turn off the axis labels
            if row != len(timeseries) - 1:
                plt.setp(t.ax.get_xticklabels(), visible=False)
            # register this in the frames dictionary
            try:
                n = t.name
                if n in self.frames:
                    n += '-{}'.format(row)
            except AttributeError:
                n = (row + hasimshow, col)
            self.frames[n] = t
