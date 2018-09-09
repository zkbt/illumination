from .IllustrationBase import *
from .CameraOfCCDsIllustration import *
from ..frames import CameraFrame, cameras

__all__ = ['FourCameraOfCCDsIllustration']


class FourCameraOfCCDsIllustration(IllustrationBase):
    '''
    For displaying a single Camera, by organizing
    individual TESS CCDs into their appropriate
    places and orientations.
    '''
    illustrationtype = 'FourCameraOfCCDs'

    def __init__(self, cam1=[], cam2=[], cam3=[], cam4=[], orientation='horizontal', sizeofcamera=4, subplot_spec=None, sharecolorbar=True, processingsteps=[],  plotingredients=['image', 'time','colorbar'], **kwargs):
        '''

        Parameters
        ----------
        cam1, etc... : various
            a dictionary with keys of 'ccd1', 'ccd2', 'ccd3', 'ccd4'
            that each contain something that can initialize a sequence

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
                                      figsize=(sizeofcamera * cols, sizeofcamera * rows * 1.25)),
                                  hspace=0.02, wspace=0.02,
                                  left=0.05, right=0.95,
                                  bottom=0.1, top=0.9,
                                  subplot_spec=subplot_spec,
                                  sharecolorbar=sharecolorbar)

        # initiate the axes for each camera
        for i in range(rows):
            for j in range(cols):



                # create a CameraFrame for this camera
                n = i * cols + j + 1
                name = 'cam{}'.format(i * cols + j + 1)
                isfullofccds = type(locals()[name]) == dict
                assert(isfullofccds)
                # kludge -- good to check, but this will break if we only have 3/4 cameras

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
                        camera=name,
                        processingsteps=processingsteps,
                        plotingredients=plotingredients,
                        **ccds)

                # kludge?! this illustration doesn't get plotted when the supersceding one is
                # thiscameraillustration.plotted = {}

                # register the CCD frames (but not the cameras)
                for k in thiscameraillustration.frames.keys():
                    framekey = '{}-{}'.format(name,k)
                    self.frames[framekey] = thiscameraillustration.frames[k]
                    self.frames[framekey].illustration = self

        self._condense_timelabels()
