from .FrameBase import FrameBase
from .imshowFrame import imshowFrame
from .CameraFrame import CameraFrame

import matplotlib.pyplot as plt
from ..utils import create_test_fits
def test_CameraFrame():
    plt.ion()
    image = create_test_fits()
    c = CameraFrame(data=image)
    c.plot()
    plt.show()
    return c
