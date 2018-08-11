from playground.imports import *
from playground.tv import *
from playground.cartoons import *


def test_timeseries():
    x = (np.linspace(0, 1) * u.day + Time.now()).jd
    y = np.random.normal(0, 1, len(x))
    f = EmptyTimeseriesFrame(ax=plt.gca())
    f.ax.plot(x, y)
    return f
