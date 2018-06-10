from __future__ import print_function
import os, copy, subprocess, glob, shutil
import numpy as np, matplotlib.pyplot as plt

import matplotlib.animation as ani
import matplotlib.gridspec as gs

from astropy.io import fits
from astropy.time import Time

from .talker import Talker

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

def shared_directory(files, verbose=False):
    '''
    Find the shared base directory amongst a list of files.

    Parameters
    ----------

    files : list
        A list of filenames.

    Returns
    -------

    shared : str
        A filepath that is the shared across all the files.
    '''

    for i in range(len(files[0])):
        shared = files[0][:i+1]
        if verbose:
            print('"{}"'.format(shared))
        for f in files:
            if f[:i+1] != shared:
                if verbose:
                    print('Huzzah! "{}" is shared across {} files.'.format(shared[:-1], len(files)))
                return shared[:-1]
