#!/usr/bin/env python
from playground.photometry import *
from playground.postage import *
from playground.tv import *
from playground.imports import *

outputdirectory = '/scratch2/zkbt/orbit-8196/analyses'
directories = glob.glob(outputdirectory, 'Central*/cam*/*/')

for d in directories:
    if len(glob.glob(os.path.join(d, 'jitter*.pdf'))) > 0:
        print('skipping {}'.format(d))
        continue
    plot_jitter_correlate(d)
    print('completed jitter plots for {}'.format(d))
