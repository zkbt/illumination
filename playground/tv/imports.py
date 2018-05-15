from __future__ import print_function
import os, copy, subprocess, glob
import numpy as np, matplotlib.pyplot as plt

import matplotlib.animation as ani
import matplotlib.gridspec as gs

from astropy.io import fits
from astropy.time import Time

def mkdir(path):
        '''
        A mkdir that doesn't complain if it already exists.
        '''
        try:
            os.mkdir(path)
            print("made {}".format(path))
        except:
            pass

def mad(x):
        '''
        Returns the median absolute deviation from the median,
                a robust estimator of a distribution's width.

                For a Gaussian distribution, sigma~1.48*MAD.
        '''
        med = np.median(x)
        return np.median(np.abs(x - med))
