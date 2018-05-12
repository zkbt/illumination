# this sets where to look for inputs and store outputs
# (it will default to `~/.tess/spyffi` if the $SPYFFIDATA environment variable isn't set)
import os
os.environ["SPYFFIDATA"] = '/Users/zkbt/Cosmos/Data/TESS/FFIs'



import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 8#'small'
mpl.rcParams['xtick.labelsize'] = 8#'small'
mpl.rcParams['ytick.labelsize'] = 8#'small'
mpl.rcParams['font.size'] = 8#'small'

#import craftroom.transit

# some basics
import numpy as np, matplotlib.pyplot as plt
import os, copy, subprocess, glob

# general tools from my library
import craftroom.utils
from craftroom.Talker import Talker

# make sure some directories exist to help out
dirs = dict(plotting='plots', cosmics='comparingcosmics')
for d in dirs.values():
    craftroom.utils.mkdir(d)
