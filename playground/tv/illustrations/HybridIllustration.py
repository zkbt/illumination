from .IllustrationBase import *

__all__ = ['HybridIllustration']

class HybridIllustration(IllustrationBase):
    illustrationtype = 'Timeseries'

    def __init__(self, imshows=[], timeseries=[], aspectratio=np.inf, **kwargs):
        '''
        Initialize an illustration from list of frames.


        '''

        # set up the geometry (imshows on time, timeseries below)
        hasimshow = int(len(imshows) > 0)
        rows = hasimshow  + len(timeseries)
        cols = np.maximum(1, len(imshows))
        height_ratios = hasimshow*[1] + len(timeseries)*[0.3]
        each = 3.2
        hspace, wspace = 0.15, 0.08
        left, right = 0.1, 0.95
        bottom, top = 0.1, 0.9
        wsize = each*cols*(1 + (cols-1)*wspace)/(right-left)
        hsize = each*np.sum(height_ratios)*(1 + (rows-1)*hspace)/(top-bottom)

        IllustrationBase.__init__(self, rows, cols,
                                    figkw=dict(figsize=(wsize, hsize)),
                                    hspace=hspace, wspace=wspace,
                                    left=left, right=right,
                                    bottom=bottom, top=top,
                                    height_ratios=height_ratios,
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
            except AttributeError:
                n = (row, col)
            self.frames[n] = i

        # add the timeseries
        sharex = None # you may want to change the shared axes for different visualizations
        for row, t in enumerate(timeseries):
            col = 0

            # make sure to connect the frame back to this illustration
            t.illustration = self
            # create the axes in which this should sit
            t.ax = plt.subplot(self.grid[row + hasimshow, :], sharex=sharex)
            sharex=t.ax

            # turn off the axis labels
            if row != len(timeseries) - 1:
                plt.setp(t.ax.get_xticklabels(), visible=False)
            # register this in the frames dictionary
            try:
                n = i.name
            except AttributeError:
                n = (row + hasimshow, col)
            self.frames[n] = t
