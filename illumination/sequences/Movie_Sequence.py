'''
Define a generic sequence of images.
'''
from .Image_Sequence import *
try:
    import imageio
except ImportError:
    pass

class Movie_Sequence(Image_Sequence):
    @property
    def N(self):
        '''
        How many frames are in this movie?
        '''
        return self.video.get_length()


    def __init__(self, filename, name='movie', time=None, temporal={}, spatial={}, **kwargs):
        '''
        Initialize a Sequence from a .MP4 or .MOV movie file.

        Parameters
        ----------
        filename : string
            The path to the movie file to open.

        time : array, None
            An array of times for the sequence.
        '''


        # hang on to the original filename
        self.filename = filename

        # set up the video reader
        self.video = imageio.get_read(filename, 'ffmpeg')

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
            # it's possible this is really slow + inefficient
            return self.get_data(timestep)
