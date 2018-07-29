from ..imports import *
from .zoom import *
from .illustrations import SingleCameraIllustration, FourCameraIllustration, SingleCameraWithZoomIllustration
from playground.postage.stamps import *

def camera_from_filename(f):
    try:
        return os.path.basename(f).split('cam')[1].split('_')[0]
    except IndexError:
        return '?'


def illustratefits(pattern='*.fits', get_camera=camera_from_filename, zoomposition=None, zoomsize=(10,10), **kw):
    '''
    Make an Illustration from a group of FITS files.

    If one (or fewer) cameras are found through
    the 'cam{}' substring, a SingleCameraIllustration illustration is returned.

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

    **kw : dict
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
            illustration = SingleCameraWithZoomIllustration(data[cam], zoomposition=zoomposition, zoomsize=zoomsize, **kw)

        else:
            illustration = SingleCameraIllustration(data[cam], **kw)

    elif len(data) > 1:
        inputs = dict(**data)
        for k in kw.keys():
            inputs[k] = kw[k]
        illustration = FourCameraIllustration(**inputs)

    return illustration


def illustratestamps(pattern='stamps/spm*/*.npy', get_camera=camera_from_filename, zoom=50, **kw):
    '''
    Make an Illustration from a group of Stamps.

    If one (or fewer) cameras are found through
    the 'cam{}' substring, a SingleCameraIllustration illustration is returned.

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
        illustration = SingleCameraIllustration(**kw)
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

def get_writer(filename, fps=30):
    '''
    Try to get an appropriate writer,
    given the filename provided.
    '''
    if '.mp4' in filename:
        try:
            writer = ani.writers['ffmpeg'](fps=fps)
        except (RuntimeError, KeyError):
            raise RuntimeError('This computer seems unable to ffmpeg.')
    else:
        try:
            writer = ani.writers['pillow'](fps=fps)
        except (RuntimeError, KeyError):
            writer = ani.writers['imagemagick'](fps=fps)
    return writer


def animate(illustration, filename='test.mp4',
            mintime=None, maxtimespan=None, cadence=2 * u.s,
            fps=30, dpi=None, **kw):
    '''
    Create an animation from an Illustration,
    using the time axes associated with each frame.

    The Illustration needs to have been plotted once already.
    '''

    # figure out the times to display
    if mintime is None:
        actualtimes, actualcadence = illustration._timesandcadence(
            round=cadence.to('s').value)
        lower, upper = min(actualtimes.gps), max(
            actualtimes.gps) + actualcadence.to('s').value
    else:
        lower = mintime.gps
        upper = lower + maxtimespan.to('s').value

    if cadence is None:
        cadence = actualcadence.to('s').value
    else:
        # np.maximum(cadence.to('s').value, actualcadence.to('s').value)
        cadence = cadence.to('s').value

    if maxtimespan is not None:
        upper = lower + np.minimum(upper - lower, maxtimespan.to('s').value)

    times = np.arange(lower, upper, cadence)
    print('animating {} times at {}s cadence for {}'.format(
        len(times), cadence, illustration))

    # get the writer
    writer = get_writer(filename, fps=fps)

    print(' to be saved at {}'.format(filename))
    # set up the animation writer
    with writer.saving(illustration.figure, filename, dpi or illustration.figure.get_dpi()):

        for i, t in enumerate(times):
            print('  {}/{} at {}'.format(i + 1,
                                         len(times), Time.now().iso), end='\r')

            # update the illustration to a new time
            illustration.update(Time(t, format='gps', scale='tdb'))

            writer.grab_frame()
