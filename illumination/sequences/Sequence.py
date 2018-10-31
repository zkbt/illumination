'''
Define a generic sequence.
'''

from ..imports import *
from ..postage.stamps import Stamp
from ..utilities import *
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
        return '<{} of {} elements>'.format(self.nametag, self.N)

    @property
    def N(self):
        '''
        How many elements are in this sequence?
        '''
        try:
            return len(self.time)
        except AttributeError:
            return 0

    def __len__(self):
        return self.N
