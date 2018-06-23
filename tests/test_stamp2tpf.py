from playground.tpf.stamps import *
from playground.tpf.tpf import EarlyTessTargetPixelFile


s = create_test_stamp()
tpf = EarlyTessTargetPixelFile.from_stamp(s)


tpf.plot()

lc = tpf.to_lightcurve()
tpf.to_lightcurve()

plt.show()
