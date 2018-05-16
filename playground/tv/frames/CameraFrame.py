from .FrameBase import *
from matplotlib.colors import SymLogNorm, LogNorm

class CameraFrame(FrameBase):

    def __init__(self, *args, **kwargs):

        FrameBase.__init__(self, *args, **kwargs)

        # tidy up the axes for this camera
        self.ax.set_aspect('equal')
        if self.data is None:
            self.axax.set_xlim(0, 4184)
            self.axax.set_ylim(0, 4184)
        plt.setp(self.axax.get_xticklabels(), visible=False)
        plt.setp(self.axax.get_yticklabels(), visible=False)
        self.ax.set_facecolor('black')
        
    def plot(self, *args, **kwargs):
        pass


    def update(self, *args, **kwargs):
        pass
