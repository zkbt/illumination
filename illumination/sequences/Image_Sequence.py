'''
Define a generic sequence of images.
'''
from .Sequence import *

class Image_Sequence(Sequence):
    def __init__(self, name='images', time=None, temporal={}, spatial={}, **kwargs):
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


        self.temporal = temporal
        self.spatial = spatial

        # pull out the shape of the array
        N, ysize, xsize = self.shape

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

    def __getitem__(self, *args, **kwargs):
        '''
        This should be written over in all sequences that inherit from this one.
        The function should return the image data for a given timestep.
        '''
        raise RuntimeError("Sorry! No image-getting procedure is defined for the generic Image_Sequence!")

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
            self.spatial['median'] = np.nanmedian(s, axis=0)
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
        return np.nansum(s, axis=0)

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
                thisimage = self[i]
                ok = np.isfinite(thisimage)
                total[ok] += thisimage[ok]

            self.spatial['mean'] = total/self.N

        return self.spatial['mean']

    def __repr__(self):
        '''
        How should this sequence be represented, by default, as a string.
        '''
        shape = self.shape
        return '<{} of {} images of shape {}>'.format(self.nametag, shape[0], shape[1:])
