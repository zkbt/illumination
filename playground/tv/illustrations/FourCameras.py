from .illustration import *
from ..frames import CameraFrame

class FourCameraIllustration(Illustration):

    def __init__(self):

        each = 4
        N = len(cubes)
        rows, cols = 1, 4

        Illustration.__init__(self, rows, cols,
                                figkw=dict(figsize=(each*len(cubes), each)),
                                hspace=0.1, left=0.05, right=0.95,
                                bottom=0.15, top=0.9)

        i = 0
        for j in range(cols):
            ax = plt.subplot(self.grid[i, j])
            ax.set_aspect('equal')
            ax.set_xlim(0, 4184)
            ax.set_ylim(0, 4184)
            self.frames[n] = Camera(ax=ax, data=None, name='CAM{}'.format(j+1))
