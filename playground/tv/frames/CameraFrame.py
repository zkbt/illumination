from .imshowFrame import *
from matplotlib.colors import SymLogNorm, LogNorm

class CameraFrame(imshowFrame):
    frametype = 'camera'

    def __init__(self, name='camera',
                       ax=None,
                       data=None,
                       **framekw):

        '''
        Initialize a CameraFrame. For plotting, this
        expects to see a full-frame image from a full
        camera (not split into CCDs.)

        Parameters
        ----------

        name : str
            A name to give this Frame.

        ax : matplotlib.axes.Axes instance
            All plotting will happen inside this ax.
            If set to None, the `self.ax attribute` will
            need to be set manually before plotting.

        data : Image_Sequence
            Any Sequence that contains 2D images.

        **framekw : dict
            Passed to imshowFrame;
            check it out for more options.
        '''

        # initialize the imshow frame
        imshowFrame.__init__(self, name=name, ax=ax, data=data, **framekw)

        # set up the basic geometry
        self.xmin, self.ymin = 0, 0
        try:
            # if there's an image, use it to set the size
            self.ymax, self.xmax = self.data[0].shape
        except (IndexError, AttributeError, TypeError):
            # allow us to create an empty image
            self.ymax = 4156
            self.xmax = 4272


### FIXME -- make sure I understand the geometry here (I don't think I do now)
class Camera1Frame(CameraFrame):

    def __init__(self, name='cam1', **kwargs):
        CameraFrame.__init__(self, name=name, **kwargs)

    def _transformimage(self, image):
        '''
        horizontal:
                (should be) +x is up, +y is left
                (looks like) +x is up, +y is right
        '''
        if self._get_orientation() == 'horizontal':
            return image.T[:, :]

    def _transformxy(self, x, y):
        '''
        This handles the same transformation as that which goes into
        transform image, but for x and y arrays.
        '''
        if self._get_orientation() == 'horizontal':
            displayy = x
            displayx = y  # self.ymax-y
        return displayx, displayy


class Camera2Frame(Camera1Frame):
    def __init__(self, name='cam2', **kwargs):
        CameraFrame.__init__(self, name=name, **kwargs)

class Camera3Frame(CameraFrame):
    def __init__(self, name='cam3', **kwargs):
        CameraFrame.__init__(self, name=name, **kwargs)

    def _transformimage(self, image):
        '''
        horizontal:
                (should be) +x is down, +y is right
                (looks like) +x is down, +y is left
        '''
        if self._get_orientation() == 'horizontal':
            return image.T[::-1, ::-1]

    def _transformxy(self, x, y):
        '''
        This handles the same transformation as that which goes into
        transform image, but for x and y arrays.
        '''
        if self._get_orientation() == 'horizontal':
            displayy = self.xmax - x
            displayx = self.ymax - y
        return displayx, displayy

class Camera4Frame(Camera3Frame):
    def __init__(self, name='cam4', **kwargs):
        CameraFrame.__init__(self, name=name, **kwargs)

# define a dictionary, so these cameras are easier to access
cameras = { 'camera': CameraFrame,
            'cam1'  : Camera1Frame,
            'cam2'  : Camera2Frame,
            'cam3'  : Camera3Frame,
            'cam4'  : Camera4Frame}
