'''
Define a generic sequence of images.
'''
from .Sequence import *
from ..cartoons import create_test_times

class Image_Sequence(Sequence):
    def __init__(self, initial, name='cube', time=None, temporal={}, spatial={}, **kwargs):
        '''
        Initialize a Sequence from a Cube.
        (a Cube is a custom, simplified, set of images)

        Parameters
        ----------
        initial : (many possible types)
            - a (ysize x = xsize)-shaped array
            - a (ntimes x ysize x = xsize)-shaped array

        time : array, None
            An array of times for the sequence.

        '''


        # create a sequence
        Sequence.__init__(self, name=name)

        # make sure we're dealing with an array
        array = np.atleast_2d(initial)

        # handle a single image as a 1-element array
        if len(array.shape) == 2:
            array = array[np.newaxis, :, :]
        elif len(array.shape) != 3:
            raise RuntimeError("The inputs to Image_Sequence seem to be the wrong shape.")

        # pull out the shape of the array
        N, ysize, xsize = array.shape
        self.images = array

        self.temporal = temporal
        self.spatial = spatial

        if time is None:
            self.time = Time(np.arange(N), format='gps', scale='tdb')
            self._timeisfake = True
        else:
            self._timeisfake = False
            assert(len(time) == N)
            if isinstance(time, Time):
                self.time = time
            else:
                self.time = Time(time, format=guess_time_format(time), scale=timescale)

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

    @property
    def shape(self):
        '''
        Returns
        -------
        s : tuple
            The shape of the image stack (ntimes x nrows x ncols)
        '''
        d = self[0]
        return (self.N, d.shape[0], d.shape[1])

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

        s = np.zeros(self.shape)
        self.speak('gathering the sequence cube, with shape {}'.format(self.shape))
        for i in range(self.N):
            self.speak(' loaded frame {}/{}'.format(i+1, self.N), progress=True)
            s[i, :, :] = self[i]
        return s

    def median(self):
        '''
        Calculate the median image.

        Returns
        -------
        median : 2D image
            The median of the image sequence.
        '''

        try:
            self.spatial['median']
        except KeyError:
            self.speak('creating a median image for {}'.format(self))
            s = self._gather_3d()
            self.spatial['median'] = np.median(s, axis=0)
        return self.spatial['median']

    def sum(self):
        '''
        Calculate the sum of all the images.

        Returns
        -------
        sum : 2D image
            The median of the image sequence.
        '''

        s = self._gather_3d()
        return np.sum(s, axis=0)

    def mean(self):
        '''
        Calculate the sum of all the images.
        It works in an inline fashion, so you
        don't need to load the entire image
        cube into memory (that might get big!)

        Returns
        -------
        mean : 2D image
            The median of the image sequence.
        '''

        try:
            self.spatial['mean']
        except KeyError:
            self.speak('creating a mean image for {}'.format(self))

            # calculate the mean in a running fashion (less memory)
            total = np.zeros_like(self[0])
            for i in range(self.N):
                self.speak(' included frame {}/{} in mean'.format(i+1, self.N), progress=True)
                total += self[i]

            self.spatial['mean'] = total/self.N

        return self.spatial['mean']

    def __repr__(self):
        '''
        How should this sequence be represented, by default, as a string.
        '''
        return '<{} of {} images of shape {}>'.format(self.nametag, self.shape[0], self.shape[1:] )
