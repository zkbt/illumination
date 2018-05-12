'''
Tools to stack images, using a variety of algorithms
(this duplicates many of the algorithms from Strategies,
so that they can be better optimized for 2D images).
'''

from .imports import *

class Stacker(Talker):
    '''Stack a cube of images, using some filter.'''

    def __init__(self, **kwargs):
        # decide whether or not this Stacker is chatty
        Talker.__init__(self, **kwargs)

    def stackCosmics(self, cube):
        pass

class Sum(Stacker):
    '''This is just a dummy to prevent the pick function from breaking when all we want is a name.'''
    def __init__(self, **kwargs):
        self.name = 'Sum'



class Central(Stacker):
    '''Binning with TruncatedMean = break into subsets, reject the highest and lowest points from each and take the mean of the rest, sum these truncated means.'''
    def __init__(self, n=10, m=None, **kwargs):
        Stacker.__init__(self)
        self.n = n
        if m is None:
            self.m = self.n-2
        else:
            self.m = m
            assert(((self.n - self.m) % 2) == 0)
        self.name = "Central {m} out of {n}".format(m = self.m, n=self.n)

    def stack(self, cube, nsubexposures):
        assert(self.n - self.m == 2)

        # figure out the original shape
        xpixels, ypixels, subexposures = cube.photons.shape
        exposures = subexposures/nsubexposures
        assert(subexposures % nsubexposures == 0)

        # reshape into something more convenient for summing
        splitintosubexposures = cube.photons.reshape(xpixels, ypixels, exposures, nsubexposures)
        splitintochunks = splitintosubexposures.reshape(xpixels, ypixels, exposures, nsubexposures/self.n, self.n)

        # calculate the sum of the truncated means (and recalibrate to the original scale!!!)
        sum = np.sum(splitintochunks, -1)
        min = np.min(splitintochunks, -1)
        max = np.max(splitintochunks, -1)
        photons = np.sum(sum - max - min, -1)*self.n/self.m

        # sum the cosmics
        cosmics = np.sum(cube.cosmics.reshape(xpixels, ypixels, exposures, nsubexposures), -1)

        # sum the noiseless image
        noiseless = np.sum(cube.noiseless.reshape(xpixels, ypixels, exposures, nsubexposures), -1)

        # sum the unmitigated image
        unmitigated = np.sum(sum, -1)
        assert((unmitigated > 1).all())

        return photons.squeeze(), cosmics.squeeze(), noiseless.squeeze(), unmitigated.squeeze()
