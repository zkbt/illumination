from .GenericIllustration import *
from ..frames import CameraFrame
from ..frames import ZoomFrame

__all__ = ['imshowWithZoomIllustration']


class imshowWithZoomIllustration(GenericIllustration):
    '''
    The imshowWithZoomeIllustration displays one imshowFrame
    and one ZoomFrame that magnifies some small region of it.
    '''
    illustrationtype = 'imshowWithZoomIllustration'

    def __init__(self, data=[], zoomposition=(0, 0), zoomsize=(10, 10), **kwargs):
        '''
        **kwargs are passed to both make_image_sequence and the frames
        '''

        # create a CameraFrame for this camera
        i_camera = CameraFrame( illustration=self,
                                data=make_image_sequence(data, **kwargs),
                                **kwargs)

        # add the ZoomFrame, connected to the camera
        i_zoom = ZoomFrame(     illustration=self,
                                source=i_camera,
                                position=zoomposition,
                                size=zoomsize,
                                **kwargs)

        GenericIllustration.__init__(self, imshows=[i_camera, i_zoom])
