from __future__ import print_function
from .filenameparsers import *
from .Image_Sequence import *


class FITS_Sequence(Image_Sequence):
    '''
    A sequence of FITS images, with a time associated with each.
    '''

    def __init__(self, initial, ext_image=1, ext_primary=0, name='FITS',
                       use_headers=True,
                       use_filenames=False,
                       filenameparser=qlp_filenameparser,
                       timekey=None, timeformat=None,
                       **kwargs):
        '''
        Initialize a Sequence of FITS images. The goal is
        to create a list of FITS HDUs, one for each time.


        Parameters
        ----------
        initial : (many possible types)
                -single FITS filename, and an extension to use.
                -list of FITS filenames, and an extension to use.
                -a glob-like search string containing '*'.
                -single FITS HDUList, and an extension to use.
                -list of loaded FITS HDULists, and an extension to use.
        '''

        # initialize the basic sequence
        Sequence.__init__(self, name=name)

        # we keep the HDUs out of memory, until we need them
        # (this should probably someday be rewritten as an iterator?)
        self._hdulists = None

        # ultimately, we want to make a list of filenames or HDULists
        if type(initial) == fits.HDUList:
            # if this is one HDUList, make it a list of them
            self._hdulists = [initial]
        elif type(initial) == str:
            # a search string
            if '*' in initial:
                self.filenames = glob.glob(initial)
                #self.hdulists = [fits.open(f) for f in glob.glob(initial)]
            # a single file
            elif 'fit' in initial.lower():
                self.filenames = [initial]
                #self.hdulists = [fits.open(initial)]
        elif type(initial) == list:
            # a list of filenames
            if np.all([type(hdu) == fits.HDUList for hdu in initial]):
                self._hdulists = initial
            elif np.all([os.path.exists(s) for s in initial]):
                self.filenames = initial

        # if we're starting frmo hdulists, then get their filenames
        if self._hdulists is not None:
            self.filenames = [h.filename() for h in self._hdulists]

        # make sure this FITS_Sequence isn't empty
        #assert(len(self.filenames) > 0)

        self.ext_primary = ext_primary
        self.ext_image = ext_image
        # if len(self.hdulists) > 0:
        #	self.ext_image = np.minimum(self.ext_image, len(self.hdulists[0]))

        self.temporal = {}
        self.static = {}
        self.spatial = {}

        # populate the temporal axes, somehow
        assert(use_headers or use_filenames)
        if use_headers:
            try:
                self._populate_from_headers()
            except:
                self.speak('unable to extract temporal things from headers for {}'.format(self))
        if use_filenames:
            try:
                self._populate_from_filenames(filenameparser=filenameparser)
            except:
                self.speak('unable to extract temporal things from filenames for {}'.format(self))

        # make sure a time axis gets defined
        self._define_time_axis(timekey=timekey, timeformat=timeformat)

        # make sure everything gets sorted by time
        self._sort()

    def sort(self):
        '''
        Sort the images, and the temporals.
        '''

        # calculate sorting indices
        i = np.argsort(self.time.gps)

        # sort the temporal values
        for k in self.temporal.keys():
            self.temporal[k] = self.temporal[k][i]

        # sort the images
        self.filenames = self.filenames[i]
        if self._hdulists is not None:
            self._hdulists = self._hdulists[i]



    @property
    def N(self):
        '''
        How many elements are in this sequence?
        '''
        return len(self.filenames)

    def _get_hdulist(self, i):
        '''
        Return an HDUlist for the ith element in the sequence.

        (We might want to open them only one at a time, for memory's sake.)
        '''
        if self._hdulists is not None:
            return self._hdulists[i]
        else:
            return fits.open(self.filenames[i], memmap=False)

    def _clean_temporal(self):
        '''
        Move anything that's non-changing from temporal to static.
        '''
        # move non-changing things to static
        for k in list(self.temporal.keys()):
            if len(np.unique(self.temporal[k])) == 1:
                self.static[k] = self.temporal.pop(k)[0]
        self.speak('the temporal keys for {} are {}'.format(self, self.temporal.keys()))
        self.speak('the static keys for {} are {}'.format(self, self.static.keys()))

    def _populate_from_filenames(self, filenameparser=qlp_filenameparser):
        '''
        Pull the basic information and temporal axis from the filenames.
        '''
        self.speak('populating {} information from the filenames (like {})'.format(self, self.filenames[0]))
        for i, f in enumerate(self.filenames):
            this = filenameparser(f)

            # create empty lists, if necessary
            if i == 0:
                for k in this.keys():
                    self.temporal[k] = []

            # tack this file onto the list
            for k in this.keys():
                self.temporal[k].append(this[k])

        # move static things away from temporal
        self._clean_temporal()

    def _populate_from_headers(self):
        '''
        Attempt to populate the sequence from the headers.
        '''

        self.speak('populating {} information from the headers'.format(self))

        # pull out the first HDUList in the sequence
        first = self._get_hdulist(0)

        # check to see if the requested image extension exists
        try:
            first[self.ext_image]
        except IndexError:
            self.speak('image extension {} not found, switching to 0'.format(self.ext_image))
            self.ext_image = 0

        # load the headers for the primary and the image
        pri, img = first[self.ext_primary].header, first[self.ext_image].header

        # if only a single image, everything is static (but can be viewed as temporal)
        if self.N == 1:
            for h in [pri, img]:
                for k in h.keys():
                    self.static[k] = h[k]
                    self.temporal[k] = [self.static[k]]
        else:

            # look through the unique extensions
            extensions = np.unique([self.ext_primary, self.ext_image])

            # create lists for each key in the headers
            for e in extensions:
                h = first[e].header
                for k in h.keys():
                    self.temporal[k] = []

            # compile all values from the headers
            for i in range(self.N):
                hdulist = self._get_hdulist(i)
                self.speak("populating header {} of {}".format(i+1, self.N), progress=True)
                for e in extensions:
                    h = hdulist[e].header
                    for k in h.keys():
                        self.temporal[k].append(h[k])

            # move static things away from temporal
            self._clean_temporal()

    def _define_time_axis(self, timekey=None, timeformat=None):

        # make up an imaginary GPS time (and keep track of whether it is fake)
        self.time = Time(np.arange(self.N), format='gps', scale='tdb')
        self._timeisfake = True

        # try to pull out a specific key
        if timekey is not None:
            self.time = Time(np.asarray(self.temporal[timekey]),
                        format=timeformat or guess_time_format(self.temporal[timekey]),
                        scale=timescale)
            self.speak('using "{}" as the time axis'.format(timekey))
        else:
            # try to pull a time axis from these
            for k in ['TIME', 'MJD', 'JD', 'BJD', 'BJD_TDB']:
                try:
                    # treat some value as a time
                    t = self.temporal[k]

                    # if it's already an astropy time, keep it as such
                    if isinstance(t, Time):
                        self.time = t
                    # make an astropy time out of the values
                    else:
                        self.time = Time(np.asarray(t),
                                    format=timeformat or guess_time_format(t),
                                    scale=timescale)
                        self._timeisfake = False
                    self.speak('guessing "{}" is good as the time axis'.format(k))
                    self._timeisfake = False
                except KeyError:
                    continue

    def __getitem__(self, timestep):
        '''
        Return the image data for a given timestep.

        This function is called when you say `sequence[timestep]`.

        Parameters
        ----------
        timestep : int
                A timestep index (which element in the sequence do you want?)
        '''
        if timestep is None:
            return None
        else:
            return self._get_hdulist(timestep)[self.ext_image].data
