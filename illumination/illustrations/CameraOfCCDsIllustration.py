from .IllustrationBase import *
from .CameraIllustration import *
from ..frames import CameraFrame, cameras
from ..frames import CCDFrame, ccds
__all__ = ['CameraOfCCDsIllustration']

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
                 subplot_spec=None,
                 camera='camera',
                 sharecolorbar=True,
                 **framekw):
        '''
        Parameters
        ----------
        ccd1, ccd2, ccd3, ccd4
            Each should be able to initialize a sequence with
            the make_image_sequence() helper function.

        data
            Will be ignored.

        orientation : str
            'horizontal' = camera 2 is right of camera 1
            'vertical'  = camera 2 is below camera 1

        sizeofcamera : float
            What's the size, in inches, to display a single camera?
            (Each CCD will be half this.)

        subplot_spec : matplotlib.gridspec.SubplotSpec
            Should this illustration go into an
            existing SubplotSpec somewhere? (Useful for
            making subillustrations of other illustrations.)

        camera : str
            We need a CameraFrame associated with this
            illustration, to be able to handle transformations
            from Camera coordinates to display coordinates.
            Specify it here via 'camera' (default, no transformation)
            or 'cam1', 'cam2', 'cam3', 'cam4'.

        **framekw passed to frame
        '''


        # set up the basic geometry of the main axes
        rows, cols = 2, 2

        # what's the orientation of this illustration?
        self.orientation = orientation

        # create the basic illustration, possibly populating an existing subplot_spec
        IllustrationBase.__init__(self, rows, cols,
                                  figkw=dict(
                                      figsize=( sizeofcamera,
                                                sizeofcamera*1.25)),
                                  hspace=0.02, wspace=0.02,
                                  left=0.05, right=0.95,
                                  bottom=0.1, top=0.9,
                                  subplot_spec=subplot_spec,
                                  sharecolorbar=sharecolorbar)

        # FIXME -- make some more precise adjustments to this
        # to ensure that the spacing between CCDs doesn't get wonky
        # We could get pretty close simply by chosing the figsize
        # carefully whenever we make one, but it'd be good to have
        # much more self-contained control over the layout within
        # this camera.

        # create a hidden frame, which we'll use for transformations
        self._cameraframe = cameras[camera](illustration=self)

        assert(self._cameraframe.name == camera)


        if self.orientation == 'horizontal':
            # start the CCDs in the orientation of
            # 2 1
            # 3 4
            loc = np.array([[0,1], [0,0], [1,0], [1,1]])

            if self._cameraframe.transpose:
                # swap CCDs diagonally
                loc = loc[[0, 3, 2, 1]]

            if self._cameraframe.flipx:
                # swap CCDs along rows
                loc = loc[[1, 0, 3, 2]]

            if self._cameraframe.flipy:
                # swap CCDs along cols
                loc = loc[[3, 2, 1, 0]]

        # populate the axes on the main camera grid
        ax = {'ccd{}'.format(i+1):plt.subplot(self.grid[loc[i][0], loc[i][1]]) for i in range(4)}

        # loop through, create a frame for each CCD
        for k in ax.keys():
            self.frames[k] = ccds[k](illustration=self,
                                     ax=ax[k],
                                     data=make_image_sequence(locals()[k]),
                                     camera=self._cameraframe,
                                     **framekw)

            # by linking this CCD to a camera, we can use its transformations
            assert(self.frames[k].camera == self._cameraframe)

        self._condense_timelabels()
