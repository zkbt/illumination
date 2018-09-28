from .imshowFrame import *
from .CameraFrame import *

class CCDFrame(CameraFrame):
    '''
    This is an imshowFrame associated with one CCD. It can
    transform from CCD coordinates to Camera coordinates.

    A single CCD can be created on its own, but more often
    it will be linked to a Camera, to continue the transformation
    onward from Camera to display.
    '''

    frametype = 'CCD'

    def __init__(self, name='ccd',
                       ax=None,
                       data=None,
                       camera=CameraFrame(),
                       **kwargs):

        # if this CCD is associated with a named camera, label in this frame
        if camera.name != 'camera':
            name = '{}-{}'.format(camera.name, name)

        # initialize the base imshowFrame, with data and a name
        imshowFrame.__init__(self, name=name, ax=ax, data=data, **kwargs)

        # make sure we're linked to a camera (for transformations)
        self.camera = camera

        # set up the sizes
        self.xmin, self.ymin = 0, 0
        try:
            # if there's an image, use it to set the size
            self.ymax, self.xmax = self.data[0].shape
        except (IndexError, AttributeError, TypeError):
            # allow us to create an empty image
            self.ymax = 2078
            self.xmax = 2136

        # set the default translation for this CCD
        self.transpose = False
        self.flipy     = False
        self.flipx     = False

        # give a non-empty string title for this CCD
        # self.titlefordisplay = self.name

    def _transformimage(self, image):
        '''
        This first transforms by the CCD's transformation to get to
        Camera coordinates, and then transforms from Camera coordinates
        to get to display coordinates.

        It reuses the definition of CameraFrame's transformations,
        but first with the (transpose,flipx,flipy) of the CCD,
        and then after with the (transpose,flipx,flipy) of the Camera.
        '''
        cameraimage = CameraFrame._transformimage(self, image)
        return self.camera._transformimage(cameraimage)

    def _transformxy(self, x, y):
        '''
        This first transforms by the CCD's transformation to get to
        Camera coordinates, and then transforms from Camera coordinates
        to get to display coordinates.

        It reuses the definition of CameraFrame's transformations,
        but first with the (transpose,flipx,flipy) of the CCD,
        and then after with the (transpose,flipx,flipy) of the Camera.
        '''

        # shrink the camera to CCD size, so we can still use it for transformations (?)
        self.camera.xmax, self.camera.ymax = self.xmax, self.ymax
        camerax, cameray = CameraFrame._transformxy(self, x, y)
        return self.camera._transformxy(camerax, cameray)

class CCD1Frame(CCDFrame):
    '''
    CCDs 1 and 2 have (0,0) in the upper right.
    '''
    def __init__(self, name='ccd1', **kwargs):
        CCDFrame.__init__(self, name=name, **kwargs)
        self.transpose = False
        self.flipy     = True
        self.flipx     = True

class CCD2Frame(CCD1Frame):
    '''
    CCDs 1 and 2 have (0,0) in the upper right.
    '''
    def __init__(self, name='ccd2', **kwargs):
        CCD1Frame.__init__(self, name=name, **kwargs)

class CCD3Frame(CCDFrame):
    '''
    CCDs 3 and 4 have (0,0) in the lower left (untransformed).
    '''
    def __init__(self, name='ccd3', **kwargs):
        CCDFrame.__init__(self, name=name, **kwargs)
        self.transpose = False
        self.flipy     = False
        self.flipx     = False

class CCD4Frame(CCD3Frame):
    '''
    CCDs 3 and 4 have (0,0) in the lower left (untransformed).
    '''
    def __init__(self, name='ccd4', **kwargs):
        CCD3Frame.__init__(self, name=name, **kwargs)

# define a dictionary, so these ccds are easier to access
ccds = {'ccd' : CCDFrame,
        'ccd1': CCD1Frame,
        'ccd2': CCD2Frame,
        'ccd3': CCD3Frame,
        'ccd4': CCD4Frame}
