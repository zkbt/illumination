from ..imports import *
from .illustrations import SingleCamera, FourCameras
from .utils import *

def camera_from_filename(f):
    try:
        return os.path.basename(f).split('cam')[1].split('_')[0]
    except IndexError:
        return '?'

def illustratefits(pattern='*.fits', get_camera=camera_from_filename, **kw):
    '''
    Make an Illustration from a group of FITS files.

    If one (or fewer) cameras are found through
    the 'cam{}' substring, a SingleCamera illustration is returned.

    If more than on cameras are found through
    the 'cam{}' substring, a FourCameras illustration is returned.

    Parameters
    ----------
    pattern : string, list
        If a string, a file-search pattern (e.g. with '*') for glob
        If a list, a list of filenames.

    get_camera : function
        Returns 1,2,3,4 or "?" based on strings in the filename.

    **kw : dict
        Keyword arguments will be passed to the Illustration

    '''

    # pull out the files
    files = glob.glob(pattern)
    data = {'cam{}'.format(c):[] for c in [1,2,3,4,'?']}

    # sort them into cameras
    for f in files:
        cam = get_camera(f)
        data['cam{}'.format(cam)].append(f)

    # remove the empty cameras
    keys = list(data.keys())
    for k in keys:
        if len(data[k]) == 0:
            data.pop(k)

    # figure out how to display them
    if len(data) == 1:
        cam = list(data.keys())[0]
        illustration = SingleCamera(data[cam], **kw)
    elif len(data) > 1:
        illustration = FourCameras(**data, **kw)

    return illustration
