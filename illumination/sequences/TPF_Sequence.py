'''
Define a sequence of images from a TPF.
'''

from .Image_Sequence import *

class TPF_Sequence(Image_Sequence):
    def __init__(self, initial, name='TPF', **kwargs):
        '''
        Initialize a Sequence from a Target Pixel File
        (see lightkurve).


        Parameters
        ----------
        initial :
                -a TargetPixelFile object
                -a filename of a TargetPixelFile

        **kwargs : dict
                Keyword arguments are stored in self.keywords.
        '''

        # make sure we have a TPF as imput
        if type(initial) == str:
            tpf = EarlyTessTargetPixelFile.from_fits(initial)
        else:
            tpf = initial

        # create a sequence out of that stamp
        Sequence.__init__(self, name=name)

        # set up the basic sequence
        self.tpf = tpf

        # pull out the time
        self.time = Time(self.tpf.time, format='jd', scale=timescale)
        self.titlefordisplay = 'TIC{}\nCAM{} | ({},{}) | {:.0f}s'.format(
            tpf.tic_id, tpf.cam, tpf.col_cent, tpf.row_cent, tpf.cadence.to('s').value)

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
            return self.tpf.flux[timestep, :, :]

    def _gather_3d(self):
        '''
        Gather a 3D cube of images.
        '''
        return self.tpf.flux[:, :, :]
