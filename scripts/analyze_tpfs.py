#!/usr/bin/env python
from playground.photometry import *
from playground.postage import *
from playground.tv import *
from playground.imports import *

# let's define a range of times
N = 1

# these are the start and end of the ranges
#start, end = 2458278.6166949864, 2458281.660259801
start = 2458278.7
end = start + 1.5
edges = np.linspace(start, end, N+1)
starts, ends = edges[:-1], edges[1:]
span = np.median(ends - starts)
print('splitting {} days {} ways leaves {:.0f}/{:.0f} (30min/2min) cadences per group'.format(end-start, N, span*24/0.5, span*24*60/2))

# set up the directories to look at
stampfiles = glob.glob('/scratch2/zkbt/orbit-8196/stamps/*/*.npy')
outputdirectory = '/scratch2/zkbt/orbit-8196/analyses'

# what strategy will we test?
strategy = Central(10)
starts = list(starts) + [-np.inf]
ends = list(ends) + [np.inf]

# loop over stamp files (these are faster to load than FITs)
np.random.shuffle(stampfiles)
for s in stampfiles:
    # loop over cadences
    for cadence in [120, 1800]:
        tic = os.path.basename(s).split('tic')[1].split('_')[0]
        search = os.path.join(outputdirectory, strategy.name.replace(' ', ''), '*tic{}*{}s'.format(tic, cadence), '*/*.mp4')
        if len(glob.glob(search)) > 0:
            print('Skipping {}. It already seems finished.'.format(s))
            continue

        # loop over time ranges
        for start, end in zip(starts, ends):

            try:
                tpf = EarlyTessTargetPixelFile.from_stamp(Stamp(s))
                tpf.to_fits(directory=outputdirectory)
                tpfs, lcs, summary, jitter = evaluate_strategy(tpf, directory=outputdirectory, cadence=cadence, strategy=strategy, start=start, end=end)
                visualize_strategy(tpfs, lcs, summary, jitter, animation=True);
            except Exception as e:
                print("Something went wrong with {}!".format(s))
                print(e)
