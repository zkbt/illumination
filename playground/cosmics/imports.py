# this sets where to look for inputs and store outputs
# (it will default to `~/.tess/spyffi` if the $SPYFFIDATA environment variable isn't set)
import os
#os.environ["SPYFFIDATA"] = '/Users/zkbt/Cosmos/Data/TESS/FFIs'

import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 8#'small'
mpl.rcParams['xtick.labelsize'] = 8#'small'
mpl.rcParams['ytick.labelsize'] = 8#'small'
mpl.rcParams['font.size'] = 8#'small'

# some basics
import numpy as np, matplotlib.pyplot as plt
import os, copy, subprocess, glob

import matplotlib.animation as ani

from .talker import Talker

def mkdir(path):
        '''
        A mkdir that doesn't complain if it already exists.
        '''
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
