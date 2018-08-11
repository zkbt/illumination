from .imshowFrame import *
from .CameraFrame import *

class CCDFrame(imshowFrame):
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

        # initialize the base imshowFrame, with data and a name
        imshowFrame.__init__(self, name=name, ax=ax, data=data, **kwargs)

        # make sure we're linked to a camera
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

class CCD1Frame(CCDFrame):
    '''
    CCDs 1 and 2 have (0,0) in the upper right.
    '''
    def __init__(self, name='ccd1', **kwargs):
        CCDFrame.__init__(self, name=name, **kwargs)

    def _transformimage(self, image):
        '''
        Transform an image from CCD to Camera coordinates,
        and then transform those Camera coordinates to display.

        (0,0) is in the upper right
        +x should increase to the left
        +y should increase down
        '''

        # get the camera image
        image_camera = image[::-1, ::-1]

        # get the display image
        return self.camera._transformimage(image_camera)

    def _transformxy(self, x, y):
        '''
        Transform an (x,y) coordinates from CCD to Camera coordinates,
        and then transform those Camera coordinates to display. This is
        the same transformation as _transformimage, but for vectors.

        (0,0) is in the upper right
        +x should increase to the left
        +y should increase down
        '''

        # get the camera coordinates
        camerax, cameray = self.xmax - x, self.ymax - y

        # get the display coordinates
        return self.camera._transformxy(camerax, cameray)


class CCD2Frame(CCD1Frame):
    '''
    CCDs 1 and 2 have (0,0) in the upper right.
    '''
    def __init__(self, name='ccd2', **kwargs):
        CCDFrame.__init__(self, name=name, **kwargs)

class CCD3Frame(CCDFrame):
    '''
    CCDs 3 and 4 have (0,0) in the lower left (untransformed).
    '''
    def __init__(self, name='ccd3', **kwargs):
        CCDFrame.__init__(self, name=name, **kwargs)

    def _transformimage(self, image):
        '''
        Transform an image from CCD to Camera coordinates,
        and then transform those Camera coordinates to display.

        (0,0) is in the upper right
        +x should increase to the left
        +y should increase down
        '''

        # get the camera image
        image_camera = image

        # get the display image
        return self.camera._transformimage(image_camera)

    def _transformxy(self, x, y):
        '''
        Transform an (x,y) coordinates from CCD to Camera coordinates,
        and then transform those Camera coordinates to display. This is
        the same transformation as _transformimage, but for vectors.

        (0,0) is in the upper right
        +x should increase to the left
        +y should increase down
        '''

        # get the camera coordinates
        camerax, cameray = x, y

        # get the display coordinates
        return self.camera._transformxy(camerax, cameray)

class CCD4Frame(CCD3Frame):
    '''
    CCDs 3 and 4 have (0,0) in the lower left (untransformed).
    '''
    def __init__(self, name='ccd4', **kwargs):
        CCDFrame.__init__(self, name=name, **kwargs)

ccds = {'ccd1': CCD1Frame,
        'ccd2': CCD2Frame,
        'ccd3': CCD3Frame,
        'ccd4': CCD4Frame}
