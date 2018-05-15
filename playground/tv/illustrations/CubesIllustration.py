from .illustration import *
class CubesIllustration(Illustration):

    def __init__(self, cubes, names=[], aspectratio=np.inf):

        each = 4
        N = len(cubes)
        cols = np.minimum(np.ceil(np.sqrt(N)*aspectratio), N).astype(np.int)
        rows = np.maximum(np.ceil(N/cols), 1).astype(np.int)
        Illustration.__init__(self, rows, cols,
                                figkw=dict(figsize=(each*len(cubes), each)),
                                hspace=0.1, left=0.05, right=0.95,
                                bottom=0.15, top=0.9)

        for i in range(rows):
            for j in range(cols):

                if len(cubes) == 0:
                    break

                ax = plt.subplot(self.grid[i, j])
                c = cubes.pop(0)
                try:
                    n = names[i*cols + j]
                except IndexError:
                    n = (i,j)

                self.frames[n] = imshowStampFrame(ax=ax, data=c, name=n)
