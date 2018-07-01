from playground.photometry import *
from playground.postage import *
from playground.tv import *
from playground.imports import *

# let's define a range of times
N = 5

# these are the start and

start, end = 2458278.6166949864, 2458281.660259801
edges = np.linspace(start, end, N+1)
starts, ends = edges[:-1], edges[1:]
span = np.median(ends - starts)
print('splitting {} days {} ways leaves {:.0f}/{:.0f} (30min/2min) cadences per group'.format(end-start, N, span*24/0.5, span*24*60/2))

stampfiles = glob.glob('/scratch2/zkbt/orbit-8196/stamps/*/*.npy')
stampfiles

starts = list(starts) + [-np.inf]
ends = list(starts) + [np.inf]
for start, end in zip(starts, ends):
    for s in stampfiles:
        tpf = EarlyTessTargetPixelFile.from_stamp(Stamp(s))
        tpfs, lcs, summary = evaluate_strategy(tpf, diretory='/scratch2/zkbt/orbit-8196/analyses', cadence=120, strategy=Central(10), start=start, end=end)
        visualize_strategy(tpfs, lcs, summary);
