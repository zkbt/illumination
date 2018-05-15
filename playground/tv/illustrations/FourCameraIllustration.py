from .IllustrationBase import *
from ..frames import CameraFrame

class FourCameraIllustration(IllustrationBase):

    def __init__(self, aspectratio=np.inf):

        each = 4
        N = 4
        cols = np.minimum(np.ceil(np.sqrt(N)*aspectratio), N).astype(np.int)
        rows = np.maximum(np.ceil(N/cols), 1).astype(np.int)
        IllustrationBase.__init__(self, rows, cols,
                                figkw=dict(figsize=(each*N, each)),
                                hspace=0.1, left=0.05, right=0.95,
                                bottom=0.15, top=0.85)


        for i in range(rows):
            for j in range(cols):
                ax = plt.subplot(self.grid[i, j])
                ax.set_aspect('equal')
                ax.set_xlim(0, 4184)
                ax.set_ylim(0, 4184)
                n = i*cols + j + 1
                self.frames[n] = CameraFrame(ax=ax, data=None, name='CAM{}'.format(n))
