from ..imports import *
from .illustrations import FourCameraIllustration
from .utils import *

def camera_from_filename(f):
    return os.path.basename(f).split('cam')[1].split('_')[0]


def showfits(pattern='*.fits', get_camera=camera):
    '''
    Maybe this should be replaced with a FITS_Sequence?
    '''

    files = glob.glob(pattern)
    data = {'cam{}'.format(c):[] for c in [1,2,3,4]}

    for f in files:
        cam = get_camera(f)
        data['cam{}'.format(cam)].append(f)

    fci = FourCameraIllustration(**data)
    return fci
