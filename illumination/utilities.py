from .imports import *

def get_writer(filename, fps=30):
    '''
    Try to get an appropriate animation writer,
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
            raise RuntimeError('This computer seem unable to animate?')
    return writer


def guess_time_format(t, default='jd'):
    '''
    For a given array of times,
    make a guess about its time format.

    Parameters
    ----------
    t : array, float
            A time, in any format. This will try to guess the format, assuming we're in the 2000s

    default : str
            The default format, if no actual choice can be made.

    Returns
    -------
    format : str
            A time format string appropriate for astropy times.
    '''

    if t is []:
        return default

    # make some string guesses
    if isinstance(t[0], str):
        if 'T' in t[0]:
            return 'isot'
        else:
            return 'iso'

    ranges = dict( gps=[0.1e9, 2e9],  # valid between 1983-03-08 09:46:59.000 and 2043-05-23 03:33:39.000
                   # valid between 1858-11-16 12:00:00.000 and 3501-08-15 12:00:00.000
                   jd=[2.4e6, 3e6],
                   mjd=[4e4, 8e4])  # valid between 1968-05-24 00:00:00.000 and 2077-11-28 00:00:00.000

    for k in ranges.keys():
        if np.min(t) >= ranges[k][0] and np.max(t) <= ranges[k][1]:
            return k

    return default
