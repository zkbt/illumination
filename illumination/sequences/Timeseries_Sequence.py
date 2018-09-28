'''
Define a timeseries sequence.
'''

from .Sequence import *

class Timeseries_Sequence(Sequence):
    '''
    NOT CURRENTLY BEING USED.
    FIXME -- add support for updating the points in a plot in time.
    '''

    def __init__(self, initial, y=None, yuncertainty=None, name='timeseries', **kwargs):
        '''
        Initialize a Sequence from some 1D timeseries.

        Parameters
        ----------
        initial : LightCruve object, or array of times (either astropy times, or in JD)
                The time values, to be plotted on the x-axis
        y : array
                The values to be plotted on the y-axis
        yuncertainty : array
                The errorbars on y (optional).
        **kwargs are passed to plt.plot()
        '''

        try:
            # is it a lightkurve?
            time = initial.time
            y = initial.flux
        except:
            time = initial

        # make sure we have a TPF as imput
        # set up the basic sequence
        if isinstance(time, Time):
            self.time = time
        else:
            self.time = Time(
                time, format=guess_time_format(time), scale=timescale)

        # store the dependent values
        self.y = y
        self.yuncertainty = yuncertainty

        # create a sequence out of that stamp
        Sequence.__init__(self, name=name)

        # set a rough title for this plot
        self.titlefordisplay = '{}'.format(self.name)

    def __getitem__(self, timestep):
        '''
        Return the image data for a given timestep.
        '''
        if timestep is None:
            return None
        else:
            return self.y[timestep, :, :]
