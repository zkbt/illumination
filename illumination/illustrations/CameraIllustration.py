from .IllustrationBase import *
from ..frames import CameraFrame, cameras
from ..frames import CCDFrame, ccds
__all__ = ['CameraIllustration']


class CameraIllustration(IllustrationBase):
    '''
    An illustration for displaying a single Camera (unrotated, untransformed).
    '''
    illustrationtype = 'CameraIllustration'

    def __init__(self,
                 data=[],
                 orientation='horizontal',
                 sizeofcamera=4,
                 subplot_spec=None,
                 **framekw):
        '''
        Parameters
        ----------
        data : various
            Anything that can initialize a sequence with
            the make_image_sequence() helper function.

            or

            a dictionary with keys of 'ccd1', 'ccd2', 'ccd3', 'ccd4'
            that each contain something that can initialize a sequence

        orientation : str
            'horizontal' = camera 2 is right of camera 1
            'vertical'  = camera 2 is below camera 1

        sizeofcamera : float
            What's the size, in inches, to display a single camera?

        **framekw passed to CameraFrame
        '''


        # set up the basic geometry of the main axes
        rows, cols = 1, 1

        # what's the orientation of this illustration?
        self.orientation = orientation

        # craete the basic illustration
        IllustrationBase.__init__(self, rows, cols,
                                  figkw=dict(
                                      figsize=( sizeofcamera * cols,
                                                sizeofcamera * rows)),
                                  hspace=0.02, wspace=0.02,
                                  left=0.05, right=0.95,
                                  bottom=0.1, top=0.9,
                                  subplot_spec=subplot_spec)

        # populate the axes on the main camera grid
        ax = plt.subplot(self.grid[0, 0])


        # create a CameraFrame for this camera
        self.frames['camera'] = CameraFrame(illustration=self,
                                            ax=ax,
                                            data=make_image_sequence(data),
                                            **framekw)
