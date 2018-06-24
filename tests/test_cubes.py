from playground.postage.cubes import *
from playground.cartoons import *

directory = 'examples/'
mkdir(directory)

def test_cube(normalization='none', **kw):
	'''
	Make a plot of the cube.
	'''
	a = create_test_array(n=600, **kw)
	unbinned = Cube(a, cadence=2)
	central = unbinned.stack(cadence=120, strategy=Central(10))
	summed = unbinned.stack(cadence=120, strategy=Sum())
	ax = unbinned.plot(normalization=normalization, alpha=0.5)
	central.plot(ax=ax, normalization=normalization, color='black', zorder=100, marker='o')
	summed.plot(ax=ax, normalization=normalization, color='red', zorder=100, marker='.', alpha=0.5)
	plt.savefig('cube-example.pdf')
	return unbinned, central, summed
