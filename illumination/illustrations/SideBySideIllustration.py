from .IllustrationBase import *

__all__ = ['GenericIllustration']


class SideBySideIllustration(IllustrationBase):
    illustrationtype = 'Timeseries'

    def __init__(self, imshows=[], timeseries=[], width_ratios = [5, 1], each = 1.0,
                                hspace=0.15, wspace =  0.08, left=0.15, right =  0.95,
                                bottom = 0.3, top=0.9, fudge=1.2, **kwargs):
        '''
        Initialize an illustration from list of frames.
        '''

        assert(len(imshows) == len(timeseries))

        # set up the geometry (imshows on time, timeseries below)
        rows = len(imshows)
        cols = 2


        wsize = each * np.sum(width_ratios) * \
            (1 + (cols - 1) * wspace) / (right - left)
        hsize = fudge * each * rows * (1 + (rows - 1) * hspace) / (top - bottom)

        IllustrationBase.__init__(self, rows, cols,
                                  figkw=dict(figsize=(wsize, hsize)),
                                  hspace=hspace, wspace=wspace,
                                  left=left, right=right,
                                  bottom=bottom, top=top,
                                  width_ratios=width_ratios,
                                  **kwargs)

        # add the imshows
        for row, i in enumerate(imshows):
            col = 1
            # make sure to connect the frame back to this illustration
            i.illustration = self
            # create the axes in which this should sit
            i.ax = plt.subplot(self.grid[row, col])

            # register this in the frames dictionary
            try:
                n = i.name
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
            t.ax = plt.subplot(self.grid[row, col], sharex=sharex)
            sharex = t.ax

            # turn off the axis labels
            if row != len(timeseries) - 1:
                plt.setp(t.ax.get_xticklabels(), visible=False)
            # register this in the frames dictionary
            try:
                n = t.name
            except AttributeError:
                n = (row, col)
            self.frames[n] = t
