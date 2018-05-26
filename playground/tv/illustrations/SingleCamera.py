from .IllustrationBase import *
from ..frames import CameraFrame

__all__ = ['SingleCamera']

class SingleCamera(IllustrationBase):
    '''
    For displaying a single Camera.
    '''

    def __init__(self, data=[], rows=1, cols=1, orientation='horizontal', sizeofcamera = 4, **kwargs):

        # set up the basic geometry of the main axes
        self.orientation = orientation
        IllustrationBase.__init__(self, rows, cols,
                                figkw=dict(figsize=(sizeofcamera*cols, sizeofcamera*rows)),
                                hspace=0.02, wspace=0.02,
                                left=0.05, right=0.95,
                                bottom=0.1, top=0.9)

        # populate the axes on the main camera grid
        ax = plt.subplot(self.grid[0,0])

        # create a CameraFrame for this camera
        self.frames['camera'] = CameraFrame(illustration=self, ax=ax, data=data, **kwargs)
