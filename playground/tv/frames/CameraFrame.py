from .imshowFrame import *
from matplotlib.colors import SymLogNorm, LogNorm

class CameraFrame(imshowFrame):

    def __init__(self, *args, **kwargs):

        imshowFrame.__init__(self, *args, **kwargs)
        
        # tidy up the axes for this camera
        self.ax.set_aspect('equal')
        #if self.data is None:
        #    self.axax.set_xlim(0, 4184)
        #    self.axax.set_ylim(0, 4184)
        plt.setp(self.ax.get_xticklabels(), visible=False)
        plt.setp(self.ax.get_yticklabels(), visible=False)
        self.ax.set_facecolor('black')
