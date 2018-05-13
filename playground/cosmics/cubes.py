'''Generate TESS pixel lightcurve cubes with dimensions (xpix)x(ypix)x(time).'''
from .imports import *
#from Strategies import *
from .stackers import Central, Sum
from .cartoon import *

timeaxis = 0
#WIP! Still need to add a method that uses the stacker to bin to another cadence.
class Cube(Talker):
	'''
	Cube to handle simulated postage stamp pixel light curves;
			has dimensions of (xpixels, ypixels, time).
	'''

	def __init__(self, photons, cadence=2):
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

		# make up a fake time axis
		# default for plotting
		self.todisplay = self.photons

		# make up a fake time axis
		self.cadence = cadence
		self.time = np.arange(self.n)*self.cadence

		# create empty (xpixels, ypixels, n)
		if self.cadence == 2:
			bits = np.float32
		else:
			bits = np.float64

		# maybe populate these later?
		# self.photons, self.cosmics, self.noiseless, self.unmitigated = np.zeros(self.shape).astype(bits), np.zeros(self.shape).astype(bits), np.zeros(self.shape).astype(bits), np.zeros(self.shape).astype(bits)

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

		# return the stacked array
		binned = Cube(array, cadence)

		return binned

	@property
	def image(self):
		try:
			return self.todisplay
		except AttributeError:
			return self.photons

	def consider(self, array=None):
		'''
		Decide what array to visualize in plots.

		Parameters
		----------

		array : 3D array to visualize
			If it's None, then revert to photons.
		'''

		if array:
			self.todisplay = array
		else:
			self.todisplay = self.photons

	def addZoom(self):
		'''
		This should create a zoomed window of a section of the image,
		at its location on the image (for looking at rotation).
		'''
		pass

	def imshow(self, timestep=0, custom=None):
		'''
		Make an imshow of a single frame of the cube.
		'''

		image = self.todisplay[timestep, :,:]
		plotted = plt.imshow(image, interpolation='nearest', origin='lower')

		return plotted


	def movie(self, array=None, filename='test.gif', limit=10):
		self.speak('displaying (up to {0:.0f} exposures) of the pixel cube'.format(limit))

		plotted = self.imshow()
		try:
			writer = ani.PillowWriter()
		except:
			writer = ani.ImageMagickWriter()

		fig = plt.figure()
		
		# the "with" construction is a little confusing, but feel free to copy and paste this
		with writer.saving(fig, filename, fig.get_dpi()):

			for i in range(self.n):
				print(i, self.n)

				# update the data to match this frame
				plotted.set_data(self.todisplay[i, :,:])

				# save this snapshot to a movie frame
				writer.grab_frame()

	"""
	@property
	def directory(self):
		'''
		Return path to a directory where this cube's data can be stored.
		'''
		dir = self.ccd.directory + 'cubes/'
		craftroom.utils.mkdir(dir)
		return dir

	@property
	def filename(self):
		'''Return a filename for saving/loading this cube.'''

		return self.directory + 'cube_{n:.0f}exp_at{cadence:.0f}s_{stacker}.npy'.format(n=self.n, cadence=self.cadence, stacker=self.stacker.name.replace(' ', ''))



	def save(self):
		'''Save this cube a 3D numpy array (as opposed to a series of FITS images).'''
		self.speak( "Saving cube to " + self.filename)
		np.save(self.filename, (self.photons, self.cosmics, self.noiseless, self.unmitigated, self.background, self.noise, self.catalog))

	def load(self, remake=False):
		'''Load this cube from a 3D numpy array, assuming one exists with the appropriate size, for this field, at this cadence, with the right number of exposures.'''
		self.speak("Trying to load simulated cube from " + self.filename)
		try:
			assert(remake==False)
			self.photons, self.cosmics, self.noiseless, self.unmitigated, self.background, self.noise, self.catalog = np.load(self.filename)
			self.speak( 'Loaded cube from ' + self.filename)
		except:
			self.speak('No saved cube was found; generating a new one.\n          (looked in {0})'.format( self.filename))
			self.simulate()
			self.save()
	"""

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
		craftroom.utils.mkdir(dir)

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

def test(normalization='none', **kw):
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

	plt.show()
	return unbinned, central, summed
