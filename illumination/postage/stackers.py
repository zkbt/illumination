'''
Tools to stack images, using a variety of algorithms
(this duplicates many of the algorithms from Strategies,
so that they can be better optimized for 2D images).
'''

from ..imports import *

__all__ = ['Central', 'Sum']

class Stacker(Talker):
    '''Stack a cube of images, using some filter.'''

    def __init__(self, **kwargs):
        # decide whether or not this Stacker is chatty
        Talker.__init__(self, **kwargs)

    def __repr__(self):
        return "<{}>".format(self.name)

    def average1d(self, array, nsubexposures=1):
        subexposures,  = array.shape
        exposures = subexposures//nsubexposures

        trim = exposures*nsubexposures
        trimmed = array[:trim]

        # reshape into something more convenient for summing
        splitintosubexposures = trimmed.reshape(exposures, nsubexposures)

        return np.sum(splitintosubexposures, 1)/nsubexposures

class Sum(Stacker):
    '''
    Binning with Sum = simply sum along the time axis.
    '''
    def __init__(self, **kwargs):
        self.name = 'Sum'

    def __call__(self, array, nsubexposures=1):
        '''
        Parameters:
        -----------
        array : a (xsize, ysize, time) array
            Probably the photons detected.
        nsubexposures : int
            How subexposures are being stacked together?
            (this will be ignored for the straight sum)
        '''

        subexposures, xpixels, ypixels = array.shape
        exposures = subexposures//nsubexposures

        trim = exposures*nsubexposures
        trimmed = array[:trim, :, :]

        # reshape into something more convenient for summing
        splitintosubexposures = trimmed.reshape(exposures, nsubexposures, xpixels, ypixels)

        return np.sum(splitintosubexposures, 1)


class Central(Stacker):
    '''
    Binning with TruncatedMean = break into subsets,
    reject the highest and lowest points from each and
    take the mean of the rest, and sum these truncated means.

    (rescales by N/M to achieve the same values as a sum)
    '''
    def __init__(self, n=10, m=None, **kwargs):
        Stacker.__init__(self)
        self.n = n
        if m is None:
            self.m = self.n-2
        else:
            self.m = m
            assert(((self.n - self.m) % 2) == 0)
        self.name = "Central {m} out of {n}".format(m = self.m, n=self.n)

    def __call__(self, array, nsubexposures):
        '''
        Parameters:
        -----------
        array : a (xsize, ysize, time) array
            Probably the photons detected.
        nsubexposures : int
            How subexposures are being stacked together?
        '''

        # this can handle only min-max rejection
        assert(self.n - self.m == 2)

        # figure out the original shape
        subexposures, xpixels, ypixels = array.shape
        exposures = subexposures//nsubexposures
        trim = exposures*nsubexposures
        trimmed = array[:trim, :, :]

        # reshape into something more convenient for summing
        splitintosubexposures = trimmed.reshape(exposures, nsubexposures, xpixels, ypixels)
        splitintochunks = splitintosubexposures.reshape( exposures, int(nsubexposures//self.n), self.n, xpixels, ypixels)

        # calculate the sum of the truncated means (and recalibrate to the original scale!!!)
        sum = np.sum(splitintochunks, 2)
        min = np.min(splitintochunks, 2)
        max = np.max(splitintochunks, 2)

        # rescale back to the original scale
        photons = np.sum(sum - max - min, 1)*self.n/self.m

        return photons.squeeze()
