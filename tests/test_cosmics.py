from playground.imports import *
from playground.tv import *
from playground.postage import *
from playground.photometry import *
from playground.cartoons import *

directory = 'examples/'
mkdir(directory)

def test_comparison(N=12000):
    print("\nTesting a cosmic comparison strategy.")
    tpf = create_test_tpf(N=N, xsize=10, ysize=10, single=True)
    tpfs, lcs, summary, jitter = evaluate_strategy(tpf, cadence=120, directory=directory)
    return visualize_strategy(tpfs, lcs, summary, jitter, animation=False)

if __name__ == '__main__':
    i = test_comparison()
