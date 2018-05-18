from ...imports import *
from ..frames import *

class IllustrationBase:
    '''
    This contains the basic layout and organization
    for a linked visualization of images.
    '''
    name = ''
    def __init__(self, nrows, ncols, figkw=dict(figsize=None, dpi=None), **kwargs):
        '''
        Initialize an Illustration,
        setting up its figure and basic layout.
        '''
        self.figure = plt.figure(**figkw)
        self.grid = gs.GridSpec(nrows, ncols, **kwargs)
        self.frames = {}

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


        alltimes = []
        for k, f in self.frames.items():
            alltimes.extend(f._gettimes())

        if round is None:
            diffs = np.diff(np.sort(alltimes))
            round = np.min(diffs[diffs > 0])

        rounded = round*np.round(np.array(alltimes)/round)
        times = np.unique(rounded)
        cadence = np.min(np.diff(times))
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
