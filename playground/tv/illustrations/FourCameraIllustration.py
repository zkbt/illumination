from .IllustrationBase import *
from ..frames import CameraFrame

def cameraname(n):
    return

class FourCameraIllustration(IllustrationBase):

    def __init__(self, orientation='horizontal'):

        # set up the basic geometry of the main axes
        sizeofcamera = 4
        N = 4
        cols = np.minimum(np.ceil(np.sqrt(N)*aspectratio), N).astype(np.int)
        rows = np.maximum(np.ceil(N/cols), 1).astype(np.int)
        IllustrationBase.__init__(self, rows, cols,
                                figkw=dict(figsize=(sizeofcamera*cols, sizeofcamera*rows)),
                                hspace=0.02, wspace=0.02,
                                left=0.05, right=0.95,
                                bottom=0.1, top=0.9)

        # initiate the axes for each camera
        for i in range(rows):
            for j in range(cols):

                # populate the axes on the main camera grid
                ax = plt.subplot(self.grid[i, j])

                # create a CameraFrame for this camera
                name = 'Camera {}'.format(i*cols + j + 1)
                self.frames[name] = CameraFrame(ax=ax, data=None, name=name)

class ZoomsIllustration(FourCameraIllustration):

    def __init__(self, stamps, **kw):

        # first, initialize the base FourCamera
        FourCameraIllustration.__init__(self, **kw)


        for i, s in enumerate(stamps):

            row, col = s.static['ROW_CENT'], s.static['COL_CENT']
            data_coords = col, row

            cam = s.static['CAM']
            print(cam)
            reference_ax = self.frames[cam].ax
            reference_fi = reference_ax.figure

            display_coords = reference_ax.transData.transform((data_coords))
            figure_coords = reference_fi.transFigure.inverted().transform(display_coords)

            print(cam, data_coords, display_coords, figure_coords)

            size = 0.2
            left, bottom = figure_coords
            width, height = size, size
            ax = plt.axes([left, bottom, width, height])

            key = 'STAMP{}'.format(i)
            self.frames[key] = imshowFrame(ax=ax, data=s, name=key)
