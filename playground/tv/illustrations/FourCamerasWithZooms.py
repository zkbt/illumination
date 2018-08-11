# still a WIP!
from .FourCameraIllustration import *


'''
class ZoomsIllustration(FourCameraIllustration):

    def __init__(self, stamps=[], **kw):

        # first, initialize the base FourCamera
        FourCameraIllustration.__init__(self, **kw)


        for i, s in enumerate(stamps):

            row, col = s.static['ROW_CENT'], s.static['COL_CENT']
            data_coords = col, row

            cam = s.static['CAM']
            self.speak(cam)
            reference_ax = self.frames[cam].ax
            reference_fi = reference_ax.figure

            display_coords = reference_ax.transData.transform((data_coords))
            figure_coords = reference_fi.transFigure.inverted().transform(display_coords)

            self.speak(cam, data_coords, display_coords, figure_coords)

            size = 0.2
            left, bottom = figure_coords
            width, height = size, size
            ax = plt.axes([left, bottom, width, height])

            key = 'STAMP{}'.format(i)
            self.frames[key] = imshowFrame(ax=ax, data=s, name=key)
'''
