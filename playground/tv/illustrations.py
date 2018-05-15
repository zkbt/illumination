from .imports import *
from .frames import *

class Illustration:
    '''
    This contains the basic layout and organization
    for a linked visualization of images.
    '''
    name = ''
    def __init__(self, figsize=None, dpi=None, *args,  **kwargs):
        '''
        Initialize an Illustration,
        setting up its figure and basic layout.
        '''
        self.figure = plt.figure(figsize=figsize, dpi=dpi)
        self.grid = gs.GridSpec(*args, **kwargs)
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



class CubesIllustration(Illustration):

    def __init__(self, cubes, names=[], aspectratio=np.inf):

        each = 4
        N = len(cubes)
        cols = np.minimum(np.ceil(np.sqrt(N)*aspectratio), N).astype(np.int)
        rows = np.maximum(np.ceil(N/cols), 1).astype(np.int)
        Illustration.__init__(self, rows, cols,
                                figsize=(each*len(cubes), each),
                                hspace=0.1, left=0.05, right=0.95,
                                bottom=0.15, top=0.9)

        for i in range(rows):
            for j in range(cols):

                if len(cubes) == 0:
                    break

                ax = plt.subplot(self.grid[i, j])
                c = cubes.pop(0)
                try:
                    n = names[i]
                except IndexError:
                    n = (i,j)

                self.frames[n] = imshowStampFrame(ax=ax, data=c, name=n)
