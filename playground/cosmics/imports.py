# this sets where to look for inputs and store outputs
# (it will default to `~/.tess/spyffi` if the $SPYFFIDATA environment variable isn't set)
#import os
#os.environ["SPYFFIDATA"] = '/Users/zkbt/Cosmos/Data/TESS/FFIs'

# some basics
import numpy as np, matplotlib.pyplot as plt
import os, copy, subprocess, glob
import matplotlib.animation as ani
from astropy.io import fits
from .talker import Talker
from __future__ import print_function

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
