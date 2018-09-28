from illumination.imports import *
from illumination.cartoons import *
from illumination.postage.tpf import EarlyTessTargetPixelFile

directory = 'examples/'
mkdir(directory)


def test_tpfbasics():
    tpf = create_test_tpf()
    tpf.plot()
    plt.savefig('examples/stamp-to-tpf.pdf')
    lc = tpf.to_lightcurve()
    ax = lc.plot(label='raw')
    lc.flatten().plot(ax, color='orange', label='flattened')
    lc.flatten().correct().plot(ax, color='blue', label='corrected')
    plt.savefig('examples/stamp-to-tpf-to-lightcurve.pdf')
    return tpf


if __name__ == '__main__':
    test_tpfbasics()
