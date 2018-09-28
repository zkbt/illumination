'''
Define a generic sequence.
'''

from ..imports import *
from ..postage.stamps import Stamp
try:
    from ..postage.tpf import EarlyTessTargetPixelFile
    from lightkurve.lightcurve import LightCurve
    from lightkurve.targetpixelfile import TargetPixelFile
except:
    raise RuntimeWarning(
        "no lightkurve found; some TPF tools may not be available")

timescale = 'tdb'
# by default, assume all times are TDB
# this is ahead of TAI by about 31.184s
# and it differs from UTC by additional leap seconds


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
    ranges = dict( gps=[0.1e9, 2e9],  # valid between 1983-03-08 09:46:59.000 and 2043-05-23 03:33:39.000
                   # valid between 1858-11-16 12:00:00.000 and 3501-08-15 12:00:00.000
                   jd=[2.4e6, 3e6],
                   mjd=[4e4, 8e4])  # valid between 1968-05-24 00:00:00.000 and 2077-11-28 00:00:00.000

    if t == []:
        return default

    for k in ranges.keys():
        if np.min(t) >= ranges[k][0] and np.max(t) <= ranges[k][1]:
            return k

    return default


class Sequence(Talker):
    '''
    A sequence of one or more images, which can be viewed (and animated) in a tv frame.
    '''

    titlefordisplay = ''
    colorbarlabelfordisplay = ''
    _timeisfake = False

    def __init__(self, name='generic', *args, **kwargs):
        Talker.__init__(self, prefixformat='{:>32}')
        self.name = name

    def cadence(self):
        '''

        Returns
        -------
        cadence : astropy Time
                A typical cadence for the sequence.
        '''

        return np.median(np.diff(self.time))

    def _find_timestep(self, time):
        '''
        Given a time, identify its index.

        Parameters
        ----------

        time : float
                A single time (in JD?).

        Returns
        -------
        index : int
                The index of the *closest* time point.
        '''

        # pull out actual times associated with this sequence
        times = self._get_times()

        # if there are no times, return nothing
        if len(times) == 0:
            return None
        else:
            # find the index of the timepoint that is closest to this one
            diff = time - times
            step = np.argmin(abs(diff))
            return step

    def _get_times(self):
        '''
        Get the available times associated with this frame.

        Returns
        -------
        times : array
                All of the times associated with this sequence.
        '''
        return self.time

    def __repr__(self):
        '''
        How should this sequence be represented, by default, as a string.
        '''
        return '<{} of {} images>'.format(self.nametag, self.N)

    @property
    def N(self):
        '''
        How many elements are in this sequence?
        '''
        try:
            return len(self.time)
        except AttributeError:
            return 0
