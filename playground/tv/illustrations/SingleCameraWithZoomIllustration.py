from .HybridIllustration import *
from ..frames import CameraFrame
from ..frames import ZoomFrame

__all__ = ['SingleCameraWithZoomIllustration']


class SingleCameraWithZoomIllustration(HybridIllustration):
    '''
    For displaying a single Camera.
    '''
    illustrationtype = 'SingleCameraWithZoomIllustration'

    def __init__(self, data=[], zoomposition=(0, 0), zoomsize=(10, 10), **kwargs):


        # create a CameraFrame for this camera
        i_camera = CameraFrame( illustration=self,
                                data=make_sequence(data, **kwargs))

        # add the ZoomFrame, connected to the camera
        i_zoom = ZoomFrame(     illustration=self,
                                source=i_camera,
                                position=zoomposition,
                                size=zoomsize)

        HybridIllustration.__init__(self, imshows=[i_camera, i_zoom])
