'''Generate TESS pixel lightcurve cubes with dimensions (xpix)x(ypix)x(time).'''
from ..imports import *
from .stackers import Central, Sum

timeaxis = 0
class Cube(Talker):
	'''
	Cube to handle simulated postage stamp pixel light curves;
			has dimensions of (xpixels, ypixels, time).
	'''
	_savable = ['photons', 'temporal', 'static', 'spatial']
	identifier = ''
	label = ''
	colorbarlabelfordisplay = ''

	def __init__(self, photons,
					   cadence=2, # what cadence is this cube (in s)
					   time=None, # array of times for the cube
					   temporal={}, # temporal variables
					   spatial={}, # spatial variables
					   static={}, # static variables
					   ):
		'''
		Initialize a cube object.

		Parameters:
		-----------

		array : (xpixels, ypixels, time) array
		cadence?
		subexposurecadence?
		'''

		# decide whether or not this Cube is chatty
		Talker.__init__(self)

		# create an observation
		self.cadence = cadence

		# store the photons as a 3D array
		self.photons = photons

		# set shapes
		self.shape = self.photons.shape
		self.n = self.shape[0]
		self.ypixels = self.shape[1]
		self.xpixels = self.shape[2]

		# store the other diagnostics (including time)
		self.temporal = temporal

		# these times are all in seconds! (probably GPS?)
		try:
			self.time = self.temporal['TIME']
		except KeyError:
			self.speak('making up imaginary times')
			self.time = Time('2018-01-01 00:00:00.000').gps + np.arange(self.n)*self.cadence
		self.spatial = spatial
		self.static = static

		# make up a fake time axis
		# default for plotting
		self.consider()
		# create a dictionary to store a bunch of summaries
		self.summaries = {}

	def __repr__(self):
		'''
		How do we print out this cube?
		'''
		return '<Cube | {} | {}s>'.format(self.shape, self.cadence)


	def stack(self, cadence, strategy=Central(n=10), plot=False):
		'''
		Stack together 2-second exposures, using some cosmic strategy.
		'''

		# by how many subexposures do we need to bin this one?
		nsubexposures = np.int(cadence/self.cadence)

		# loop over the x and y pixels
		self.speak('binning {0} cube by {1} subexposures'.format(self.shape, nsubexposures))

		# make the stacked array
		array = strategy(self.photons, nsubexposures)

		temporal = {}
		for k in self.temporal.keys():
			temporal[k] = strategy.average1d(self.temporal[k], nsubexposures)

		static = dict(**self.static)
		# return the stacked array

		binned = Cube(array, cadence, temporal=temporal, spatial=self.spatial, static=self.static)

		return binned

	def consider(self, what='counts'):
		'''
		Decide what array to visualize in plots.

		Parameters
		----------

		what : str
			Describe what should be visualized.

		'''

		if what == 'photons':
			self.todisplay = self.photons
			#def label(i=0):
			#	return '{}s (photons)'.format(self.temporal['TIME'][i])
			self.colorbarlabelfordisplay = 'counts'

		if what == 'counts':
			# kludge! (because don't have calibrated data yet!)
			self.todisplay = self.photons
			#def label(i=0):
			#	return '{}s (counts)'.format(self.temporal['TIME'][i])
			self.colorbarlabelfordisplay = 'counts'

		if what == 'differences':
			self.todisplay = np.diff(self.photons, axis=0)
			#def label(i=0):
			#	return '{}s - {}s (counts)'.format(self.temporal['TIME'][i+1], self.temporal['TIME'][i])
			self.colorbarlabelfordisplay = 'difference (counts)'

	@property
	def titlefordisplay(self):
		'''
		What to be displayed as a title for a plot
		(this should probably be moved to a Frame instead?)
		'''
		return '{}\n{}'.format(self.identifier, self.label)

	def imshow(self, timestep=0, nsigma=0.5):
		'''
		Make an imshow of a single frame of the cube.
		'''

		a = self.todisplay
		vmin, vmax = np.percentile(a, [1,99])
		if (self.todisplay < 0).any():
			scale = np.maximum(np.abs(vmin), np.abs(vmax))
			vmin, vmax = -scale, scale

			sigma = mad(self.todisplay)
			norm = SymLogNorm(nsigma*sigma, linscale=2, vmin=vmin, vmax=vmax)
			cmap = 'RdBu'
			ticks = [vmin, -nsigma*sigma, 0, nsigma*sigma, vmax]
		else:
			norm = LogNorm(vmin=vmin, vmax=vmax)
			cmap = 'Blues'
			ticks = [vmin, vmax]

		# point at a particular image
		image = self.todisplay[timestep, :,:]

		plotted = plt.imshow(image, interpolation='nearest', origin='lower', norm=norm, cmap=cmap)
		plt.title(self.titlefordisplay)
		plt.axis('off')
		colorbar = plt.colorbar(plotted, orientation='horizontal', label=self.colorbarlabelfordisplay(0), fraction=0.04, pad=0.02, ticks=ticks)
		colorbar.ax.set_xticklabels(['{:.0f}'.format(v) for v in ticks])
		colorbar.outline.set_visible(False)

		return plotted, colorbar


	def movie(self, filename='test.gif', fps=30, **kw):
		self.speak('displaying {} exposures of the pixel cube'.format(self.n))

		plt.clf()
		plotted, colorbar = self.imshow(**kw)

		if '.mp4' in filename:
			writer = ani.writers['ffmpeg'](fps=fps)
		else:
			try:
				writer = ani.writers['pillow'](fps=fps)
			except (RuntimeError, KeyError):
				writer = ani.writers['imagemagick'](fps=fps)

		fig = plt.gcf()

		# the "with" construction is a little confusing, but feel free to copy and paste this
		with writer.saving(fig, filename, fig.get_dpi()):

			for i in range(self.todisplay.shape[0]):
				print(i, self.n)

				# update the data to match this frame
				plotted.set_data(self.todisplay[i, :,:])
				colorbar.set_label(self.colorbarlabelfordisplay(i))
				# save this snapshot to a movie frame
				writer.grab_frame()

	def cubify(self, image):
		'''
		Slightly reshape an image by adding an extra dimension,
		so it can be cast into operations on the whole cube.
		'''
		return image.reshape(1, self.xpixels, self.ypixels)

	def median(self, which='photons'):
		'''
		The median image.
		'''
		array = self.__dict__[which].astype(np.float64)
		key = 'median'
		try:
			self.summaries[key+which]
		except:
			self.summaries[key+which] = np.median(array, timeaxis)
		return self.summaries[key+which]

	def mean(self, which='photons'):
		'''
		The mean image.
		'''
		array = self.__dict__[which].astype(np.float64)
		key = 'mean'
		try:
			self.summaries[key+which]
		except:
			self.summaries[key+which] = np.mean(array, timeaxis)
		return self.summaries[key+which]


	def mad(self, which='photons'):
		'''
		The median of the absolute deviation image.
		'''
		array = self.__dict__[which].astype(np.float64)
		key = 'mad'
		try:
			self.summaries[key+which]
		except:
			self.summaries[key+which] = np.median(np.abs(array - self.cubify(self.median(which))), timeaxis)
		return self.summaries[key+which]

	def std(self, which='photons'):
		'''
		The standard deviation image.
		'''
		array = self.__dict__[which].astype(np.float64)
		key = 'std'
		try:
			self.summaries[key+which]
		except:
			self.summaries[key+which] = np.std(array, timeaxis)
		return self.summaries[key+which]

	def sigma(self, which='photons', robust=True):
		'''
		The sigma of the image, using either a robust MAD or not.
		'''
		if robust:
			return 1.4826*self.mad(which)
		else:
			return self.std(which)

	def oneWeirdTrickToTrimCosmics(self, threshold=4):
		'''
		To be used for simulating ground-based cosmics removal.

		(this assumes *zero* jitter)
		'''
		shape = np.array(self.photons.shape)
		shape[timeaxis] = 1
		bad = self.photons > (self.median() + threshold*self.sigma(robust=True)).reshape(shape)
		x, y, z = bad.nonzero()
		self.photons[x,y,z] = self.median()[x,y]
		self.speak('trimmed {0} cosmics from cube!'.format(np.sum(bad)))

	def master(self, which='photons'):
		'''
		The (calculated) master frame.
		'''
		return self.median(which)

	def nsigma(self, which='photons', robust=True):
		'''
		Calculate the number of sigma of each deviation from the median.
		'''
		array = self.__dict__[which].astype(np.float64)
		return (array - self.cubify(self.median(which)))/self.cubify(self.sigma(which, robust=robust))

	def write(self, normalization='none', directory='cube'):
		'''
		Save all the images to FITS, inside the cube directory.
		'''

		# make a directory for the normalization used
		dir = self.directory + normalization + '/'
		mkdir(dir)

		if normalization == 'none':
			flux = self.photons
		if normalization == 'nsigma':
			flux = self.nsigma()

		# loop through the images in the cube
		mkdir(directory)
		for i in range(self.n):
			# pick some kind of normalization for the image
			image = flux[i, :,:]

			filename = os.path.join(directory, normalization + '_{0:05.0f}.fits'.format(i))
			hdu = astropy.io.fits.PrimaryHDU(image)
			hdu.writeto(filename, overwrite=True)



			self.ccd.writeToFITS(image, filename)


	def plot(self, ax=None, normalization='none', ylim=[None, None], color='gray', **kw):

		# choose how to normalize the lightcurves for plotting
		if normalization.lower() == 'none':
			normalizationarray = self.cadence
			ylabel = 'Photons/s'
		elif normalization.lower() == 'master':
			normalizationarray = self.master().reshape(1, self.ypixels, self.xpixels)
			ylabel='Relative Flux'
		elif normalization.lower() == 'median':
			normalizationarray = self.median().reshape(1, self.ypixels, self.xpixels)
			ylabel='Relative Flux'

		# create a relative light curve (dF/F, in most cases)
		photonsnormalized = self.photons/normalizationarray


		# set up a logarithmic color scale (going between 0 and 1)
		# (I think this could be done better with a Norm/cmap)
		def cmap(x):
			zero = np.min(np.log(self.master()*0.5))
			span = np.max(np.log(self.master())) - zero
			#normalized = (np.log(x) -  zero)/span
			normalized = (np.log(x) -  zero)/span
			return plt.matplotlib.cm.Blues_r(normalized)
			#return plt.matplotlib.cm.YlGn(normalized)

		# create a plot
		scale = 1.5

		# set up the axes, if they don't already exist
		if ax is None:
			plt.figure('{} | normalization={}'.format(self, normalization),
						figsize = (self.xpixels*scale,self.ypixels*scale), dpi=72)
			gs = plt.matplotlib.gridspec.GridSpec(self.ypixels, self.xpixels, wspace=0, hspace=0)
			ax = {}
			a = None

			# loop over pixels (in x and y directions)
			for i in range(self.ypixels):
				for j in range(self.xpixels):

					# set up axis sharing, so zooming on one plot zooms the other
					ax[(i,j)] = plt.subplot(gs[-(i+1),j], sharex=a, sharey=a)
					a = ax[(i,j)]


					# color the plot panel based on the pixel's intensity
					a.patch.set_facecolor(cmap(self.median()[i,j]))

					# mess with the labels
					if i == 0 and j == 0:
						plt.setp(a.get_xticklabels(), rotation=90)
						a.set_xlabel('Time (s)')
						a.set_ylabel(ylabel)
					else:
						plt.setp(a.get_xticklabels(), visible=False)
						plt.setp(a.get_yticklabels(), visible=False)

		# loop over pixels (in x and y directions)
		for i in range(self.ypixels):
			for j in range(self.xpixels):
				ax[(i,j)].plot(self.time, photonsnormalized[:,i,j], color=color, **kw)

		# set the ylimits, if available
		#if ylim is None:
		#	ax.set_ylim(np.min(photonsnormalized), np.max(photonsnormalized))
		#else:
		ax[(i,j)].set_ylim(*ylim)

		return ax
