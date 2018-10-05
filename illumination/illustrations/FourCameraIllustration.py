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
        '''

        Parameters
        ----------
        cam1, etc... : various
            Anything that can initialize a sequence with
            the make_image_sequence() helper function.

        orientation : str
            'horizontal' = camera 2 is right of camera 1
            'vertical'  = camera 2 is below camera 1 (not yet implemented)

        sizeofcamera : float
            What's the size, in inches, to display a single camera?
        '''

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

                # populate the axes on the main camera grid
                ax = plt.subplot(self.grid[i, j])

                self.frames[name] = cameras[name](
                    ax=ax, data=locals()[name], illustration=self, **kwargs)
