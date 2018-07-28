from .Sequence import *


class Image_Sequence(Sequence):
    '''
    This isn't a standalone. Other image sequences inherit from it.
    '''

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
        for i in range(self.data.N):
            s[i, :, :] = self.data[i]
        return s

    def median(self):
        '''
        Calculate the median image.

        Returns
        -------
        median : 2D image
            The median of the image sequence.
        '''

        s = self._gather_3d()
        return np.median(s, axis=0)

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

        Returns
        -------
        sum : 2D image
            The median of the image sequence.
        '''

        s = self._gather_3d()
        return np.mean(s, axis=0)
