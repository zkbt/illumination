'''
Wrappers to define some default visualizations.
'''

from __future__ import print_function

from .imports import *
from .zoom import *
from .illustrations import CameraIllustration, FourCameraIllustration, SingleCameraWithZoomIllustration
from .postage.stamps import *

def camera_from_filename(f):
    try:
        return os.path.basename(f).split('cam')[1][0]
    except IndexError:
        return '?'

def illustratefits(pattern='*.fits', get_camera=camera_from_filename, zoomposition=None, zoomsize=(10,10), **illustrationkw):
    '''
    Make an Illustration from a group of FITS files.

    If one (or fewer) cameras are found through
    the 'cam{}' substring, a CameraIllustration illustration is returned.

    If more than on cameras are found through
    the 'cam{}' substring, a FourCameraIllustration illustration is returned.

    Parameters
    ----------
    pattern : string, list
        If a string, a file-search pattern (e.g. with '*') for glob
        If a list, a list of filenames.

    get_camera : function
        Returns 1,2,3,4 or "?" based on strings in the filename.

    zoomposition : tuple
        (x,y) position of where a zoom should be placed

    zoomsize : tuple
        (x,y) size of the zoom window to create

    **illustrationkw : dict
        Keyword arguments will be passed to the Illustration

    '''

    # pull out the files
    if type(pattern) == list:
        files = pattern
    else:
        files = list(np.sort(glob.glob(pattern)))
    data = {'cam{}'.format(c): [] for c in [1, 2, 3, 4, '?']}

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
        if zoomposition is not None:
            illustration = SingleCameraWithZoomIllustration(data[cam], zoomposition=zoomposition, zoomsize=zoomsize, **illustrationkw)

        else:
            illustration = CameraIllustration(data[cam], **illustrationkw)

    elif len(data) > 1:
        inputs = dict(**data)
        for k in illustrationkw.keys():
            inputs[k] = illustrationkw[k]
        illustration = FourCameraIllustration(**inputs)

    return illustration

def illustratestamps(pattern='stamps/spm*/*.npy', get_camera=camera_from_filename, zoom=50, **kw):
    '''
    Make an Illustration from a group of Stamps.

    If one (or fewer) cameras are found through
    the 'cam{}' substring, a CameraIllustration illustration is returned.

    If more than on cameras are found through
    the 'cam{}' substring, a FourCameraIllustration illustration is returned.

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
    data = {'cam{}'.format(c): [] for c in [1, 2, 3, 4, '?']}

    # sort them into cameras
    for f in files:
        cam = get_camera(f)
        data['cam{}'.format(cam)].append(f)

    # remove the empty cameras
    keys = list(data.keys())
    for k in keys:
        if len(data[k]) == 0:
            data.pop(k)

    singlecamera = len(data) == 1
    # figure out how to display them
    if singlecamera:
        cam = 'camera'
        illustration = CameraIllustration(**kw)
    elif len(data) > 1:
        cam = None
        illustration = FourCameraIllustration(**kw)
    else:
        return

    for k in data.keys():
        stamps = [Stamp(f) for f in data[k]]
        for s in stamps:
            if singlecamera:
                camera = 'camera'
            else:
                camera = 'cam{}'.format(s.cam)
            frame = add_stamp(illustration, s, zoom=zoom, camera=camera)
    return illustration
