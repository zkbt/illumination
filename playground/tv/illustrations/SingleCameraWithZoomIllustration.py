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

    def __init__(self, data=[], zoomposition=(0, 0), zoomsize=(10, 10), orientation='horizontal', sizeofcamera=4, **kwargs):


        # set up the basic geometry of the main axes
        rows, cols = 1, 2
        aspectratio = float(zoomsize[1])/zoomsize[0]
        hspace, wspace = 0.02, 0.02
        left, right = 0.05, 0.95
        bottom, top = 0.1, 0.9
        width_ratios=[1, aspectratio]


        self.orientation = orientation
        IllustrationBase.__init__(self, rows, cols,
                                  figkw=dict(
                                      figsize=(sizeofcamera * (1+aspectratio)*(1+hspace)/(right - left), sizeofcamera/(top-bottom))),
                                      hspace=hspace, wspace=wspace,
                                      left=left, right=right,
                                      bottom=bottom, top=top, width_ratios=width_ratios)

        # populate the axes on the main camera grid

        # create a CameraFrame for this camera
        self.frames['camera'] = CameraFrame(illustration=self,
                                            ax=plt.subplot(self.grid[0, 0]),
                                            data=make_sequence(data),
                                            **kwargs)

        # add the zoom frame
        self.frames['zoom'] = ZoomFrame(illustration=self,
                                        ax=plt.subplot(self.grid[0, 1]),
                                        source=self.frames['camera'],
                                        position=zoomposition,
                                        size=zoomsize)
