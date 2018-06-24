from playground.imports import *
from playground.tpf.stamps import *
from playground.tpf.tpf import EarlyTessTargetPixelFile

directory = 'examples/'
mkdir(directory)

s = create_test_stamp()
tpf = EarlyTessTargetPixelFile.from_stamp(s)
tpf.plot()
plt.savefig('examples/stamp-to-tpf.pdf')
tpf.to_lightcurve().plot()
plt.savefig('examples/stamp-to-tpf-to-lightcurve.pdf')
