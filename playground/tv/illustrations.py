from .imports import *
from .frames import *

class Illustration:
    '''
    This contains the basic layout and organization
    for a linked visualization of images.
    '''
    name = ''
    def __init__(self, *args, figsize=None, dpi=None, **kwargs):
        self.figure = plt.figure(figsize=figsize, dpi=dpi)
        self.grid = gs.GridSpec(*args, **kwargs)
        self.frames = {}

    def _timesandcadence(self, round=1):
        '''
        Get all the unique times available, and a suggested cadence.
        '''
        alltimes = []
        for k, f in self.frames.items():
            alltimes.extend(f._gettimes())
        rounded = round*np.round(np.array(alltimes)/round)
        times = np.unique(rounded)
        cadence = np.min(np.diff(times))
        return times, cadence




    def plot(self, *args, **kwargs):
        for k, f in self.frames.items():
            f.plot(*args, **kwargs)


class imshowCubes(Illustration):

    def __init__(self, cubes, names=[]):

        each = 4
        Illustration.__init__(self, 1, len(cubes),
                                figsize=(each*len(cubes), each),
                                hspace=0.04, left=0.05, right=0.95,
                                bottom=0.12, top=0.98)

        for i, c in enumerate(cubes):
            ax = plt.subplot(self.grid[0, i])
            try:
                n = names[i]
            except IndexError:
                n = ''

            self.frames[i] = imshowStampFrame(ax=ax, data=c, name=n)
