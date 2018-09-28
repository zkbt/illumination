'''
Frames each have a .plot and .update method associated with them,
meaning that they can be included and animated inside a structured
Illustration.
'''

from .FrameBase import FrameBase
from .imshowFrame import imshowFrame
from .CameraFrame import CameraFrame, cameras
from .CCDFrame import CCDFrame, ccds
from .ZoomFrame import ZoomFrame
from .LocalZoomFrame import LocalZoomFrame
from .LocalStampFrame import LocalStampFrame
from .EmptyTimeseriesFrame import EmptyTimeseriesFrame
