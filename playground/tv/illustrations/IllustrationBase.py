from ..imports import *
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

    def _timesandcadence(self, round=1.0):
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
