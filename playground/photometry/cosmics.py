from ..imports import *
from ..postage import *
from .apertures import *



def compare(filename):
    s = Stamp(filename)
    raw = EarlyTessTargetPixelFile.from_stamp(s)
