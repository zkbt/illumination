from .IllustrationBase import *
from ..frames import CameraFrame
from ..frames import ZoomFrame
from . import SingleCameraIllustration

__all__ = ['SingleCameraWithZoomIllustration']


class SingleCameraWithZoomIllustration(SingleCameraIllustration):
    '''
    For displaying a single Camera.
    '''
    illustrationtype = 'SingleCameraWithZoomIllustration'

    def __init__(self, data=[], zoomposition=(0, 0), zoomsize=(10, 10), **kwargs):

        SingleCameraIllustration.__init__(self,  data, cols=2, **kwargs)

        ax = plt.subplot(self.grid[0, 1])
        self.frames['zoom'] = ZoomFrame(illustration=self,
                                        ax=ax,
                                        source=self.frames['camera'],
                                        position=zoomposition,
                                        size=zoomsize)
