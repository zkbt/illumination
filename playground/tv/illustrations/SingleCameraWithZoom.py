from .IllustrationBase import *
from ..frames import CameraFrame
from ..frames import ZoomFrame
from . import SingleCamera

class SingleCameraWithZoom(SingleCamera):
    '''
    For displaying a single Camera.
    '''

    def __init__(self, data, zoomposition=(0,0), zoomsize=(10,10), **kwargs):

        SingleCamera.__init__(self,  data, cols=2, **kwargs)


        ax = plt.subplot(self.grid[0,1])
        self.frames['zoom'] = ZoomFrame(illustration=self,
                                        ax=ax,
                                        source=self.frames['camera'],
                                        position=zoomposition,
                                        size=zoomsize)
