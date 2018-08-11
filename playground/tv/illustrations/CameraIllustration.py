from .IllustrationBase import *
from ..frames import CameraFrame
from ..frames import CCDFrame
__all__ = ['CameraIllustration', 'CameraOfCCDsIllustration']





class CameraIllustration(IllustrationBase):
    '''
    An illustration for displaying a single Camera (unrotated, untransformed).
    '''
    illustrationtype = 'CameraIllustration'

    def __init__(self,
                 data=[],
                 orientation='horizontal',
                 sizeofcamera=4,
                 **kwargs):
        '''
        Parameters
        ----------
        data : various
            Anything that can initialize a sequence with
            the make_sequence() helper function.

            or

            a dictionary with keys of 'ccd1', 'ccd2', 'ccd3', 'ccd4'
            that each contain something that can initialize a sequence


        orientation : str
            'horizontal' = camera 2 is right of camera 1
            'vertical'  = camera 2 is below camera 1

        sizeofcamera : float
            What's the size, in inches, to display a single camera?

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
                                  )

        # populate the axes on the main camera grid
        ax = plt.subplot(self.grid[0, 0])


        # create a CameraFrame for this camera
        self.frames['camera'] = CameraFrame(illustration=self,
                                            ax=ax,
                                            data=make_sequence(data),
                                            **kwargs)

class CameraOfCCDsIllustration(CameraIllustration):
    '''
    An illustration for displaying a single Camera (unrotated, untransformed).
    '''
    illustrationtype = 'CameraOfCCDsIllustration'

    def __init__(self,
                 ccd1=[], ccd2=[], ccd3=[], ccd4=[],
                 data=[],
                 orientation='horizontal',
                 sizeofcamera=4,
                 **kwargs):
        '''
        Parameters
        ----------
        ccd1, ccd2, ccd3, ccd4
            Each should be able to initialize a sequence with
            the make_sequence() helper function.

        data
            Will be ignored.

        orientation : str
            'horizontal' = camera 2 is right of camera 1
            'vertical'  = camera 2 is below camera 1

        sizeofcamera : float
            What's the size, in inches, to display a single camera?
            (Each CCD will be half this.)

        **kwargs are passed to make_sequence
        '''


        # set up the basic geometry of the main axes
        rows, cols = 2, 2

        # what's the orientation of this illustration?
        self.orientation = orientation

        # craete the basic illustration
        IllustrationBase.__init__(self, rows, cols,
                                  figkw=dict(
                                      figsize=( sizeofcamera,
                                                sizeofcamera*1.2)),
                                                 hspace=0.02, wspace=0.02,
                                                 left=0.05, right=0.95,
                                                 bottom=0.1, top=0.9,
                                  )

        # populate the axes on the main camera grid

        ax = {  'ccd1':plt.subplot(self.grid[0,1]),
                'ccd2':plt.subplot(self.grid[0,0]),
                'ccd3':plt.subplot(self.grid[1,0]),
                'ccd4':plt.subplot(self.grid[1,1])}

        for k in ax.keys():
            self.frames[k] = ccds[k](illustration=self,
                                     ax=ax[k],
                                     data=make_sequence(locals()[k], **kwargs))
