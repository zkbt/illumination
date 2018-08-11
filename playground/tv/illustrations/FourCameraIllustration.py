from .IllustrationBase import *
from .CameraIllustration import *
from ..frames import CameraFrame, cameras

__all__ = ['FourCameraIllustration']


class FourCameraIllustration(IllustrationBase):
    '''
    For displaying a single Camera.
    '''
    illustrationtype = 'FourCamera'

    def __init__(self, cam1=[], cam2=[], cam3=[], cam4=[], orientation='horizontal', sizeofcamera=4, subplot_spec=None, **kwargs):

        # set up the basic geometry of the main axes
        sizeofcamera = 4
        N = 4
        self.orientation = orientation
        if self.orientation == 'horizontal':
            cols = N
            rows = 1
        IllustrationBase.__init__(self, rows, cols,
                                  figkw=dict(
                                      figsize=(sizeofcamera * cols, sizeofcamera * rows * 1.2)),
                                  hspace=0.02, wspace=0.02,
                                  left=0.05, right=0.95,
                                  bottom=0.1, top=0.9,
                                  subplot_spec=subplot_spec)

        # initiate the axes for each camera
        for i in range(rows):
            for j in range(cols):

                # create a CameraFrame for this camera
                n = i * cols + j + 1
                name = 'cam{}'.format(i * cols + j + 1)

                # if it's CCDs, make a four-CCD sub-illustration
                if type(locals()[name]) == dict:

                    # make a camera frame to contain these CCDs
                    cameraframe = cameras[name](ax=None,
                                                data=None,
                                                illustration=self,
                                                **kwargs)

                    # this should be a dictionary of CCDs
                    ccds = locals()[name]

                    # use an illustration to place a camera in this subplot spec
                    thiscameraillustration = CameraOfCCDsIllustration(
                            orientation=orientation,
                            sizeofcamera=sizeofcamera,
                            subplot_spec=self.grid[i,j],
                            **ccds)

                    # register the CCD frames (but not the cameras)
                    for k in thiscameraillustration.frames.keys():
                        self.frames['{}-{}'.format(name,k)] = thiscameraillustration.frames[k]

                # otherwise, simply make a frame for each camera
                else:

                    # populate the axes on the main camera grid
                    ax = plt.subplot(self.grid[i, j])

                    self.frames[name] = cameras[name](
                        ax=ax, data=locals()[name], illustration=self, **kwargs)
