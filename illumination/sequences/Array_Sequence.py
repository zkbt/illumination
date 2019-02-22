'''
Define a generic sequence of images.
'''
from .Image_Sequence import *

class Array_Sequence(Image_Sequence):
    def __init__(self, initial, name='array', time=None, temporal={}, spatial={}, **kwargs):
        '''
        Initialize a Sequence from 2D or 3D numpy array.

        Parameters
        ----------
        initial : 2D/3D numpy array, or list of numpy arrays
            - a (ysize x = xsize)-shaped array = single image
            - a (ntimes x ysize x = xsize)-shaped array = multiple images

        time : array, None
            An array of times for the sequence.
        '''



        # make sure we're dealing with an array
        array = np.atleast_2d(initial)

        # handle a single image as a 1-element array
        if len(array.shape) == 2:
            array = array[np.newaxis, :, :]
        elif len(array.shape) != 3:
            raise RuntimeError("The inputs to Image_Sequence seem to be the wrong shape.")

        # store the (now 3D) array as the images
        self.images = array

        # create a sequence
        Image_Sequence.__init__(self, name=name, time=time, temporal=temporal, spatial=spatial)



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
            return self.images[timestep, :, :]

    def _gather_3d(self):
        '''
        Gather a 3D cube of images.

        This will generally work, but it
        may be faster if you already have
        access to the full 3D array stored
        in memory (as in a Stamp or TPF).

        Returns
        -------
        s : array
        The image stack, with shape (ntimes x nrows x ncols)
        '''

        # for an array, we're already 3D!
        s = self.images
        return s


    def mean(self):
        '''
        Calculate the sum of all the images.
        It works in an inline fashion, so you
        don't need to load the entire image
        cube into memory (that might get big!)

        Returns
        -------
        mean : 2D image
            The mean of the image sequence.
        '''

        return np.mean(self.images, 0)
