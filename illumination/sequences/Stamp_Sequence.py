'''
Define a sequence of images from a Stamp object.
'''
from .Image_Sequence import *
from ..postage.stamps import *

class Stamp_Sequence(Image_Sequence):
    def __init__(self, initial, name='Stamp', **kwargs):
        '''
        Initialize a Sequence from a Stamp.
        (a Stamp is a custom, simplified version of a TPF)

        Parameters
        ----------
        initial : (many possible types)
                -a single Stamp object
                -something that can initialize a Stamp
                        A filename for a '.npy' file.
                        A list of FITS sparse_subarray files.
                        A search path of FITS sparse_subarray files (e.g. containing *.fits)

        **kwargs : dict
                Keyword arguments are passed to Stamp(initial, **kwargs)
        '''

        # make sure we have at least a stamp
        if isinstance(initial, Stamp) or isinstance(initial, Cube):
            stamp = initial
        elif (type(initial) == str) or (type(initial) == list):
            stamp = Stamp(initial, **kwargs)


        # create a sequence out of that stamp
        Sequence.__init__(self, name=name)

        # (not coincidentally), a Stamp has similar variables to a Sequence
        for k in stamp._savable:
            vars(self)[k] = vars(stamp)[k]

        # set up the basic sequence, including the time array
        self.stamp = stamp
        if isinstance(self.stamp.time, Time):
            self.time = self.stamp.time
        else:
            self.time = Time(self.stamp.time, format=guess_time_format(
                self.stamp.time), scale=timescale)

    def __getitem__(self, timestep):
        '''
        Return the image data for a given timestep.

        This function is called when you say `sequence[timestep]`.

        Parameters
        ----------
        timestep : int
                A timestep index (which element in the sequence do you want?)
        '''
        if timestep is None:
            return None
        else:
            return self.stamp.todisplay[timestep, :, :]

    def _gather_3d(self):
        '''
        Gather a 3D cube of images.
        '''
        return self.stamp.todisplay[:, :, :]

    @property
    def titlefordisplay(self):
        return self.stamp.titlefordisplay

    @property
    def colorbarlabelfordisplay(self):
        return self.stamp.colorbarlabelfordisplay
