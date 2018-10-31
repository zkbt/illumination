'''
Wrappers to define some default visualizations.
'''

from __future__ import print_function

from .imports import *
from .zoom import *
from .illustrations import *
from .postage.stamps import *
from .sequences import *

def camera_from_filename(f):
    '''
    Try to guess the camera from the filename.

    Parameters
    ----------

    filename : str
        The name of a fits file, with 'cam?' in it somewhere.
    '''

    try:
        return os.path.basename(f).split('cam')[1][0]
    except IndexError:
        return '?'

def organize_sequences(pattern='*.fits',
                       filenameparser=flexible_filenameparser,
                       ext_image=1, use_headers=False, use_filenames=True,
                       timekey='cadence'):
    '''
    Take a group of filenames, and group them in
    one of the following ways:

    1) a dictionary (with camera as key)
       of lists of filenames
    2) a dictionary (with camera as key)
       of dictionaries (with ccd as key)
       of lists of filenames

    Parameters
    ----------
    pattern : str, list
        If a string, a file-search pattern (e.g. with '*') for glob
        If a list, a list of filenames.

    filenameparser : function
        This is a function that takes in a filename,
        and returns a dictionary that contains (maybe)
        a "camera" keyword with an integer camera number
        and a "ccd" keyword with an integer ccd number.
        It is used to decide how to group images.

     ext_image=0, use_headers=False, use_filenames=True,
    '''

    # create a list of filenames
    if type(pattern) == list:
        # if given a list, use those as the filenames
        filenames = pattern
    else:
        # if given a string, use it as a glob search string
        filenames = list(np.sort(glob.glob(pattern)))

    # create an empty dictionary of cameras + CCDs
    cameras = {'cam{}'.format(c):{
                    'ccd{}'.format(d):[] for d in [1,2,3,4,'?']}
               for c in [1,2,3,4,'?']}

    # loop through images, and figure out where they belong
    for f in filenames:

        # parse the filename into a dictionary
        i = filenameparser(f)

        # figure out an appropriate camera key
        if 'camera' in i:
            camerakey = 'cam{}'.format(i['camera'])
        else:
            camerakey = 'cam?'

        # figure out an appropriate CCD key
        if 'ccd' in i:
            ccdkey = 'ccd{}'.format(i['ccd'])
        else:
            ccdkey = 'ccd?'

        # store the filename into its appropriate key
        cameras[camerakey][ccdkey].append(f)

    # convert each list of filenames into a sequence
    sequences = {}
    for camerakey in cameras.keys():
        sequences[camerakey] = {}
        for ccdkey in cameras[camerakey].keys():
            files = cameras[camerakey][ccdkey]
            if len(files) != 0:
                sequences[camerakey][ccdkey] = make_image_sequence(files,
                                                   ext_image=ext_image,
                                                   use_headers=use_headers,
                                                   use_filenames=use_filenames,
                                                   timekey=timekey)


    # if there aren't multiple CCDs, compress each camera to single list
    organized = {}
    for camerakey in sequences.keys():
        keys = list(sequences[camerakey].keys())
        if len(keys) == 1:
            organized[camerakey] = sequences[camerakey][keys[0]]
        elif len(keys) > 1:
            organized[camerakey] = sequences[camerakey]
    print('yo!')
    # return the grouped filenames
    return organized


def illustratefits( pattern='*.fits',
                    zoomposition=None, zoomsize=(10,10),
                    filenameparser=flexible_filenameparser,
                    **illustrationkw):
    '''
    Make an Illustration from a group of FITS files.

    If one (or fewer) camera is found (by parsing the filename),
    then a CameraIllustration is returned.

    If multiple cameras are found (by parsing the filename),
    then a FourCameraIllustration is returned.

    If multiple cameras and multiple CCDs are found (by parsing the filename),
    then a FourCameraOfCCDsIllustration is returned.

    Parameters
    ----------
    pattern : string, list
        If a string, a file-search pattern (e.g. with '*') for glob
        If a list, a list of filenames.

    zoomposition : tuple
        (x,y) position of where a zoom should be placed

    zoomsize : tuple
        (x,y) size of the zoom window to create

    **illustrationkw : dict
        Keyword arguments will be passed to the Illustration
    '''

    # make a "group" of filenames (either a list, a dictionary, a dictionary of dictionares)
    data = organize_sequences(pattern, filenameparser=filenameparser)
    assert(type(data) == dict)

    # is there only a single camera represented?
    singlecamera = len(data) == 1

    def merge_inputs(kw):
        # a small tool to merge dictionaries of inputs
        # (because Python 2 can't handle `**data,**inputs` in functions)
        inputs = dict(**kw)
        for k in illustrationkw.keys():
            inputs[k] = illustrationkw[k]
        return inputs

    # display these data, one way or another
    if singlecamera:
        # (there's only one camera we're trying to display)

        # pull out the (only) sequence
        cam = list(data.keys())[0]
        if type(data[cam]) is dict:
            # (one camera, and it has multiple CCDs)
            illustration = CameraOfCCDsIllustration(**merge_inputs(data[cam]))
        else:
            # (one camera, with one pseudo-CCD)
            seq = data[cam]
            if zoomposition is not None:
                # display the single image, with a zoom box added
                illustration = SingleCameraWithZoomIllustration(seq, zoomposition=zoomposition, zoomsize=zoomsize, **illustrationkw)
            else:
                # display the single image, just by itself
                illustration = CameraIllustration(seq, **illustrationkw)
            # the zoom option works only for single-frame illustrations (FIXME?)
    elif len(data) > 1:
        # (there are multiple cameras to display)

        # figure out if there's one or more CCDs
        multipleccds = False
        for k in data.keys():
            multipleccds = multipleccds or (type(data[k]) is dict)

        if multipleccds:
            # (multiple cameras, and each is multiple CCDs)
            illustration = FourCameraOfCCDsIllustration(**merge_inputs(data))
        else:
            # (multiple cameras, and each is one psuedo-CCD)
            illustration = FourCameraIllustration(**merge_inputs(data))


    return illustration

def illustratestamps(pattern='stamps/spm*/*.npy', get_camera=camera_from_filename, zoom=50, **kw):
    '''
    FIXME -- I'm not positive this still works.

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
