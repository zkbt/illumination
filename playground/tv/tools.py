from ..imports import *
from .illustrations import FourCameraIllustration

def showfits(pattern='*.fits'):
    '''
    Maybe this should be replaced with a FITS_Sequence?
    '''

    files = glob.glob(pattern)
    data = {'cam{}'.format(c):[] for c in [1,2,3,4]}

    for f in files:
        cam = [os.path.basename(f).split('cam')[1].split('_')]
        data['cam{}'.format(cam)].append(f)

    fci = FourCameraIllustration(**data)
    return fci
