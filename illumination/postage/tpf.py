from ..imports import *

from lightkurve.targetpixelfile import TargetPixelFile, KeplerTargetPixelFile, KeplerTargetPixelFileFactory, KeplerQualityFlags
from lightkurve import KeplerLightCurve, TessLightCurve
import datetime, warnings
from tqdm import tqdm


import os
TESSTPFDIR = os.path.abspath(os.path.dirname(__file__))


class EarlyTessLightCurve(KeplerLightCurve):
    def __init__(self, time, flux=None, flux_err=None,  tic_id=None, cam=None, spm=None, col_cent=None, row_cent=None, mission='TESS', **kwargs):
        self.tic_id = tic_id
        self.cam = cam
        self.spm = spm
        self.col_cent = col_cent
        self.row_cent = row_cent
        self.mission = mission
        KeplerLightCurve.__init__(self, time=time, flux=flux, flux_err=flux_err,  **kwargs)
        self.time_format = 'jd'
        self.time_scale = 'tdb'

    def plot(self, ax=None, xlabel='Time (days)', **kwargs):
        return KeplerLightCurve.plot(self, ax=None,  xlabel=xlabel, **kwargs)

    @property
    def cadence(self):
        return np.median(np.diff(self.time))*u.day


class EarlyTessTargetPixelFile(KeplerTargetPixelFile):
    """
    Defines a TargetPixelFile class for early (MIT) TESS data.
    Right now, this is based off '*_sparse_subarrays.fits' files,
    which may have been processed into Stamp objects. They can
    be loaded via the .from_stamp or .from_sparse_subarrays
    methods.

    Enables extraction of raw lightcurves and centroid positions,
    and some nice simple visualizations.
    """

    def __init__(self, *args, **kwargs):
        # KLUDGE, to make sure a flux gets defined, even for uncalibrated data
        KeplerTargetPixelFile.__init__(self, *args, **kwargs)
        if np.sum(np.isfinite(self.flux)) == 0:
            self.hdu[1].data['FLUX'] = self.raw_cnts

    @property
    def raw_cnts(self):
        return self.hdu[1].data['RAW_CNTS']

    @property
    def cadence(self):
        return np.median(np.diff(self.time))*u.day

    @property
    def background_mask(self):
        return self.hdu[-1].data == 2

    def filelabel(self, label=None):
        '''
        TESS-specific file label.
        '''
        s = 'cam{}_spm{}_tic{}_col{}_row{}_{:.0f}s'.format(self.cam, self.spm, self.tic_id, self.col_cent, self.row_cent, self.cadence.to('s').value)
        if label is not None:
            s = label + '_' + s
        return s

    def to_fits(self, output_fn=None, overwrite=False, directory='.', label=None, zip=True):
        """Writes the TPF to a FITS file on disk."""

        # set the output filename
        if output_fn is None:
            output_fn = os.path.join(directory, "{}-targ.fits".format(self.filelabel(label=label)))

        # skip writing the file, if a zipped one already exists
        if zip:
            if overwrite == False:
                zipped_fn = output_fn + '.gz'
                if os.path.exists(zipped_fn):
                    print('{} already exists! not overwriting!'.format(zipped_fn))
                    return

        # write the fits file
        try:
            self.hdu.writeto(output_fn, overwrite=overwrite, checksum=True)
        except OSError:
            print('(I think) {} already exists! not overwriting!'.format(output_fn))
        if zip:
            os.system('gzip -v {}'.format(output_fn))


    def to_lightcurve(self, aperture_mask='pipeline'):
        """Performs aperture photometry.

        Parameters
        ----------
        aperture_mask : array-like, 'pipeline', or 'all'
            A boolean array describing the aperture such that `False` means
            that the pixel will be masked out.
            If the string 'all' is passed, all pixels will be used.
            The default behaviour is to use the Kepler pipeline mask.

        Returns
        -------
        lc : KeplerLightCurve object
            Array containing the summed flux within the aperture for each
            cadence.
        """
        aperture_mask = self._parse_aperture_mask(aperture_mask)
        if aperture_mask.sum() == 0:
            log.warning('Warning: aperture mask contains zero pixels.')
        centroid_col, centroid_row = self.estimate_centroids(aperture_mask=aperture_mask)
        keys = {'centroid_col': centroid_col,
                'centroid_row': centroid_row,
                'quality': self.quality,
                'mission': self.mission,
                'cadenceno': self.cadenceno,
                'cam':self.cam,
                'spm':self.spm,
                'col_cent':self.col_cent,
                'row_cent':self.row_cent,
                'tic_id':self.tic_id}

        return EarlyTessLightCurve( time=self.time,
                                    flux=np.nansum(self.flux[:, aperture_mask], axis=1),
                                    flux_err=np.nansum(self.flux_err[:, aperture_mask]**2, axis=1)**0.5,
                                    **keys)

    def differences(self, **kwargs):
        '''
        NEW!

        Calculate the differences between subsequent images,
        and return a new TPF.
        '''
        n_cadences, n_rows, n_cols = self.shape
        tic_id = self.tic_id


        print('making TPF from the differences of {}'.format(self))
        # create a factory to populate with pixels
        factory = EarlyTessTargetPixelFileFactory(n_cadences=n_cadences-1,
                                                   n_rows=n_rows,
                                                   n_cols=n_cols,
                                                   target_id=tic_id)

        # a stamp already exists, so we can add everything all at once
        factory.keywords = fits.Header(self.hdu[0].header)
        #factory.raw_cnts = np.diff(self.raw_cnts, axis=0)
        factory.flux = np.diff(self.flux, axis=0)
        #factory.flux_bkg = np.diff(self.flux_bkg, axis=0)

        # set some variables in the time dimension
        factory.time = 0.5*(self.time[1:] + self.time[:-1])
        factory.cadenceno = np.arange(len(factory.time))
        factory.quality = self.quality[1:] | self.quality[:-1]

        return factory.get_tpf(**kwargs)

    @staticmethod
    def from_archive(target, cadence='long', quarter=None, month=None,
                     campaign=None, radius=1., targetlimit=1, verbose=True, **kwargs):
        """
        There's no archive yet!
        """
        raise ValueError("There's no TESS archive yet!")

    def __repr__(self):
        return('EarlyTessTPF Object (TIC{})'.format(self.tic_id))

    def get_prf_model(self):
        """
        FIXME! This should turn into a very simple (Gaussian)
        and then slightly more complicated (database) PRF at some pointself.

        Returns an object of SimpleKeplerPRF initialized using the
        necessary metadata in the tpf object.

        Returns
        -------
        prf : instance of SimpleKeplerPRF
        """

        raise RuntimeWarning("PRF not yet made for TESS!")

        return SimpleKeplerPRF(channel=self.channel, shape=self.shape[1:],
                               column=self.column, row=self.row)

    @property
    def astropy_time(self):
        """Returns an AstroPy Time object for all good-quality cadences."""
        return Time(self.time, format='jd', scale='tdb')

    @property
    def tic_id(self):
        self.header['TIC_ID']

    @property
    def cam(self):
        return self.header['CAM']

    @property
    def spm(self):
        return self.header['SPM']

    @property
    def col_cent(self):
        return self.header['COL_CENT']

    @property
    def row_cent(self):
        return self.header['ROW_CENT']

    # add a thing to make reasonable WCS for each stamp -- can this be tied to TIC location + aperture definition?

    def plot(self, *args, **kwargs):
        """
        Plot a target pixel file at a given frame (index) or cadence number.

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            A matplotlib axes object to plot into. If no axes is provided,
            a new one will be generated.
        frame : int
            Frame number. The default is 0, i.e. the first frame.
        cadenceno : int, optional
            Alternatively, a cadence number can be provided.
            This argument has priority over frame number.
        bkg : bool
            If True, background will be added to the pixel values.
        aperture_mask : ndarray
            Highlight pixels selected by aperture_mask.
        show_colorbar : bool
            Whether or not to show the colorbar
        mask_color : str
            Color to show the aperture mask
        style : str
            matplotlib.pyplot.style.context, default is 'fast'
        kwargs : dict
            Keywords arguments passed to `lightkurve.utils.plot_image`.

        Returns
        -------
        ax : matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes object.
        """
        ax = KeplerTargetPixelFile.plot(self, *args, **kwargs)
        ax.set_title('TIC: {}'.format(self.tic_id))
        return ax

    @staticmethod
    def from_fits_images(images, position=None, size=(10, 10), extension=None,
                         target_id="unnamed-target", **kwargs):
        """
        work-in-progress -- (e.g. to extract single stamps from FFIs)

        Creates a new Target Pixel File from a set of images.

        This method is intended to make it easy to cut out targets from
        Kepler/K2 "superstamp" regions or TESS FFI images.

        Attributes
        ----------
        images : list of str, or list of fits.ImageHDU objects
            Sorted list of FITS filename paths or ImageHDU objects to get
            the data from.
        position : astropy.SkyCoord
            Position around which to cut out pixels.
        size : (int, int)
            Dimensions (cols, rows) to cut out around `position`.
        extension : int or str
            If `images` is a list of filenames, provide the extension number
            or name to use. Default: 0.
        target_id : int or str
            Unique identifier of the target to be recorded in the TPF.
        **kwargs : dict
            Extra arguments to be passed to the `KeplerTargetPixelFile` constructor.

        Returns
        -------
        tpf : KeplerTargetPixelFile
            A new Target Pixel File assembled from the images.
        """
        if extension is None:
            if isinstance(images[0], str) and images[0].endswith("ffic.fits"):
                extension = 1  # TESS FFIs have the image data in extension #1
            else:
                extension = 0  # Default is to use the primary HDU

        factory = EarlyTessTargetPixelFileFactory(n_cadences=len(images),
                                                   n_rows=size[0],
                                                   n_cols=size[1],
                                                   target_id=target_id)
        for idx, img in tqdm(enumerate(images), total=len(images)):
            if isinstance(img, fits.ImageHDU):
                hdu = img
            elif isinstance(img, fits.HDUList):
                hdu = img[extension]
            else:
                hdu = fits.open(img)[extension]
            if idx == 0:  # Get default keyword values from the first image
                factory.keywords = hdu.header
            if position is None:
                cutout = hdu
            else:
                cutout = Cutout2D(hdu.data, position, wcs=WCS(hdu.header),
                                  size=size, mode='partial')
            factory.add_cadence(frameno=idx, flux=cutout.data, header=hdu.header)
        return factory.get_tpf(**kwargs)

    @staticmethod
    def from_stamp(stamp, **kwargs):

        """
        Creates a new Target Pixel File from a stamp.

        Attributes
        ----------
        stamp : a stamp object
        **kwargs : dict
            Extra arguments to be passed to the `EarlyTessTargetPixelFile` constructor.

        Returns
        -------
        tpf : EarlyTessTargetPixelFile
            A new Target Pixel File assembled from the images.
        """

        n_cadences, n_rows, n_cols = stamp.photons.shape
        tic_id = stamp.static['TIC_ID']


        print('making TPF from {}'.format(stamp)
        )
        # create a factory to populate with pixels
        factory = EarlyTessTargetPixelFileFactory(n_cadences=n_cadences,
                                                   n_rows=n_rows,
                                                   n_cols=n_cols,
                                                   target_id=tic_id)

        # a stamp already exists, so we can add everything all at once
        factory.keywords = fits.Header(stamp.static)
        factory.raw_cnts = stamp.photons
        factory.flux = stamp.photons

        # set some variables in the time dimension

        gpstime = stamp.temporal['TIME']
        factory.time = Time(gpstime, format='gps', scale='tdb').jd
        factory.cadenceno = np.arange(len(gpstime))#stamp.temporal['CADENCE']
        factory.quality = stamp.temporal['QUAL_BIT']

        return factory.get_tpf(**kwargs)


    @staticmethod
    def from_sparse_subarrays(images,      # each image is a time-point
                              extension=1, # each extension is a stamp
                              target_id="unnamed-target",
                              **kwargs):
        """
        WIP?
        Creates a new Target Pixel File from a set of sparse images.
        This is meant to be mostly a tool to be run through all
        extensions of a sparse subarray, to create stamps that
        are saved as actual TPF files, indexed either by TIC or
        by camera coordinates.

        Attributes
        ----------
        images : list of str, or list of fits.ImageHDU objects
            Sorted list of FITS filename paths or ImageHDU objects to get
            the data from.
        extension : int or str
            Which extension (aka stamp) to extract?
        target_id : int or str
            Unique identifier of the target to be recorded in the TPF.
        **kwargs : dict
            Extra arguments to be passed to the `EarlyTessTargetPixelFile` constructor.

        Returns
        -------
        tpf : EarlyTessTargetPixelFile
            A new Target Pixel File assembled from the images.
        """

        #  we need an extension > 1 to get
        assert(extension > 0)

        # open the first one, to get the shape of the image
        first = fits.open(images[0])[extension]
        singleheader = first.header
        singleimage = first.data

        tic_id = singleheader['TIC_ID']
        '''

        size = singleimage.shape[0]
        array = np.empty((N, data.shape[0], data.shape[1]))
        oned = {}
        keys = ['INT_TIME', 'QUAL_BIT', 'TIME', 'CADENCE']
        for k in keys:
            oned[k] = np.empty(N)

        tic = header['TIC_ID']
        location = header['COL_CENT'], header['ROW_CENT']
        '''


        print('making TPF from ext={} of {} files'.format(extension, len(images)))
        # create a factory to populate with pixels
        factory = EarlyTessTargetPixelFileFactory(n_cadences=len(images),
                                                   n_rows=singleimage.shape[0],
                                                   n_cols=singleimage.shape[1],
                                                   target_id=tic_id)

        for idx, img in enumerate(tqdm(images)):

            # allow us to send hdu lists or filenames
            if isinstance(img, fits.HDUList):
                hdus = img
            else:
                hdus = fits.open(img)

            stamphdu = hdus[extension]
            framehdu = hdus[0]


            if idx == 0:  # Get default keyword values from the first image
                factory.keywords = framehdu.header
                for k in stamphdu.header.keys():
                    factory.keywords[k] = stamphdu.header[k]

            # original times are in GPS seconds
            gpstime = framehdu.header['TIME']

            # let's convert them to jd
            framehdu.header['TIME'] = Time(gpstime, format='gps', scale='tdb').jd

            # add this cadence to the TOP
            factory.add_cadence(frameno=idx, raw_cnts=stamphdu.data, flux=stamphdu.data, header=framehdu.header)

        return factory.get_tpf(**kwargs)

    @property
    def keplerid(self):
        return None


class EarlyTessTargetPixelFileFactory(KeplerTargetPixelFileFactory):
    def add_cadence(self, frameno, raw_cnts=None, flux=None, flux_err=None,
                    flux_bkg=None, flux_bkg_err=None, cosmic_rays=None,
                    header={}):
        """Populate the data for a single cadence."""
        # 2D-data
        for col in ['raw_cnts', 'flux', 'flux_err', 'flux_bkg',
                    'flux_bkg_err', 'cosmic_rays']:
            if locals()[col] is not None:
                vars(self)[col][frameno] = locals()[col]

        # 1D-data
        if 'TIME' in header:
            # FIXME -- currently GPS time (is it start/mid/end of exposure?)
            self.time[frameno] = header['TIME']

        if 'TIMECORR' in header:
            self.timecorr[frameno] = header['TIMECORR']
        if 'CADENCE' in header:
            self.cadenceno[frameno] = header['CADENCE']
        if 'QUALITY' in header:
            self.quality[frameno] = header['QUAL_BIT']

        # FIXME -- figure out how to deal with positions?
        if 'POSCORR1' in header:
            self.pos_corr1[frameno] = 0# header['POSCORR1']
        if 'POSCORR2' in header:
            self.pos_corr2[frameno] = 0# header['POSCORR2']


    def get_tpf(self, **kwargs):
        """Returns a KeplerTargetPixelFile object."""

        # FIXME -- storing the factory is just for debugging
        tpf = EarlyTessTargetPixelFile(self._hdulist(), **kwargs)
        tpf.factory = self
        return tpf

    def _header_template(self, extension):
        """
        Returns a template `fits.Header` object for a given extension,
        specifically tweaked for Early TESS objects.
        """
        template_fn = os.path.join(TESSTPFDIR, "data",
                                   "tpf-ext{}-header.txt".format(extension))
        return fits.Header.fromtextfile(template_fn)


    ### FIXME! You need to understand the header templates!
    def _make_primary_hdu(self, hdu0_keywords={}, keywords={}, **kw):
        """Returns the primary extension (#0)."""
        hdu = fits.PrimaryHDU()
        # Copy the default keywords from a template file from the MAST archive
        tmpl = self._header_template(0)
        for kw in tmpl:
            hdu.header[kw] = (tmpl[kw], tmpl.comments[kw])
        # Override the defaults where necessary
        hdu.header['ORIGIN'] = "Unofficial data product"
        hdu.header['DATE'] = datetime.datetime.now().strftime("%Y-%m-%d")
        hdu.header['CREATOR'] = "lightkurve"
        hdu.header['OBJECT'] = self.target_id
        hdu.header['TIC_ID'] = self.target_id

        # Empty a bunch of keywords rather than having incorrect info
        for kw in ["PROCVER", "FILEVER", "CHANNEL", "MODULE", "OUTPUT",
                   "TIMVERSN", "CAMPAIGN", "DATA_REL", "TTABLEID",
                   "RA_OBJ", "DEC_OBJ"]:
            hdu.header[kw] = ""


        # FIXME -- (probably a kludge, maybe we need these only in ext=1)
        template = self._header_template(0)
        for kw in template:
            if kw not in ['XTENSION', 'NAXIS1', 'NAXIS2', 'CHECKSUM', 'BITPIX']:
                try:
                    hdu.header[kw] = (self.keywords[kw],
                                      self.keywords.comments[kw])
                except KeyError:
                    #print("Couldn't add [{}]".format(kw))
                    hdu.header[kw] = (template[kw],
                                      template.comments[kw])

        return hdu

    def _make_target_extension(self, **kw):
        """Create the 'TARGETTABLES' extension (i.e. extension #1)."""
        # Turn the data arrays into fits columns and initialize the HDU
        coldim = '({},{})'.format(self.n_cols, self.n_rows)
        eformat = '{}E'.format(self.n_rows * self.n_cols)
        jformat = '{}J'.format(self.n_rows * self.n_cols)
        cols = []

        # FIXME -- may need to modify this?
        cols.append(fits.Column(name='TIME', format='D', unit='spacecraft seconds',
                                array=self.time))
        cols.append(fits.Column(name='TIMECORR', format='E', unit='D',
                                array=self.timecorr))
        cols.append(fits.Column(name='CADENCENO', format='J',
                                array=self.cadenceno))
        cols.append(fits.Column(name='RAW_CNTS', format=jformat,
                                unit='count', dim=coldim,
                                array=self.raw_cnts))

        # FIXME -- at some point, switch these to being calibrated
        cols.append(fits.Column(name='FLUX', format=eformat,
                                unit='count', dim=coldim,
                                array=self.flux))
        cols.append(fits.Column(name='FLUX_ERR', format=eformat,
                                unit='count', dim=coldim,
                                array=self.flux_err))
        cols.append(fits.Column(name='FLUX_BKG', format=eformat,
                                unit='count', dim=coldim,
                                array=self.flux_bkg))
        cols.append(fits.Column(name='FLUX_BKG_ERR', format=eformat,
                                unit='count', dim=coldim,
                                array=self.flux_bkg_err))
        cols.append(fits.Column(name='COSMIC_RAYS', format=eformat,
                                unit='count', dim=coldim,
                                array=self.cosmic_rays))
        cols.append(fits.Column(name='QUALITY', format='J',
                                array=self.quality))
        cols.append(fits.Column(name='POS_CORR1', format='E', unit='pixels',
                                array=self.pos_corr1))
        cols.append(fits.Column(name='POS_CORR2', format='E', unit='pixels',
                                array=self.pos_corr2))
        coldefs = fits.ColDefs(cols)
        hdu = fits.BinTableHDU.from_columns(coldefs)

        # Set the header with defaults
        template = self._header_template(1)
        for kw in template:
            if kw not in ['XTENSION', 'NAXIS1', 'NAXIS2', 'CHECKSUM', 'BITPIX']:
                try:
                    hdu.header[kw] = (self.keywords[kw],
                                      self.keywords.comments[kw])
                except KeyError:
                    #print("Couldn't add [{}]".format(kw))
                    hdu.header[kw] = (template[kw],
                                      template.comments[kw])

        # Override the defaults where necessary
        hdu.header['EXTNAME'] = 'TARGETTABLES'
        hdu.header['OBJECT'] = self.target_id
        hdu.header['TIC_ID'] = self.target_id
        for n in [5, 6, 7, 8, 9]:
            hdu.header["TFORM{}".format(n)] = eformat
            hdu.header["TDIM{}".format(n)] = coldim
        hdu.header['TFORM4'] = jformat
        hdu.header['TDIM4'] = coldim

        return hdu
