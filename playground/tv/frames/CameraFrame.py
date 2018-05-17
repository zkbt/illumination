from .FrameBase import *
from matplotlib.colors import SymLogNorm, LogNorm

class CameraFrame(FrameBase):

    def __init__(self, *args, **kwargs):

        FrameBase.__init__(self, *args, **kwargs)

        # tidy up the axes for this camera
        self.ax.set_aspect('equal')
        if self.data is None:
            self.axax.set_xlim(0, 4184)
            self.axax.set_ylim(0, 4184)
        plt.setp(self.axax.get_xticklabels(), visible=False)
        plt.setp(self.axax.get_yticklabels(), visible=False)
        self.ax.set_facecolor('black')

    def plot(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

def create_test_camera_images(rows=400, cols=600, visualize=False):
    x, y = np.meshgrid(np.arange(cols).astype(np.float), np.arange(rows).astype(np.float))
    sigma = 50
    z = 1.0/np.sqrt(2*np.pi)/sigma*np.exp(-0.5*(x**2 + y**2)/sigma**2)
    if visualize:

        plt.subplot(131)
        plt.imshow(x, origin='lower')
        plt.title('x')
        plt.subplot(132)
        plt.imshow(y, origin='lower')
        plt.title('y')
        plt.subplot(133)
        plt.title('z')
        plt.imshow(z, origin='lower')

    return x, y, z

x, y, z = create_test_camera_images()
plt.ion()
