from lightkurve.targetpixelfile import KeplerTargetPixelFile, KeplerTargetPixelFileFactory, KeplerQualityFlags
from lightkurve import KeplerLightCurve, TessLightCurve
from ..imports import *
import datetime, warnings


import os
TESSTPFDIR = os.path.abspath(os.path.dirname(__file__))


class EarlyTessLightCurve(KeplerLightCurve):
    def __init__(self, *args, ticid=None, camera=None, spm=None, col_cent=None, row_cent=None, mission='TESS', **kwargs):
        self.ticid = ticid
        self.camera = camera
        self.spm = spm
        self.col_cent = col_cent
        self.row_cent = row_cent
        self.mission = mission
        KeplerLightCurve.__init__(self, *args, **kwargs)
        self.time_format = 'jd'
        self.time_scale = 'tdb'

    def plot(self, *args, xlabel='Time (days)', **kwargs):
        KeplerLightCurve.plot(self, *args, **kwargs, xlabel=xlabel)


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
        centroid_col, centroid_row = self.centroids(aperture_mask)
        keys = {'centroid_col': centroid_col,
                'centroid_row': centroid_row,
                'quality': self.quality,
                'mission': self.mission,
                'cadenceno': self.cadenceno,
                'camera':self.camera,
                'spm':self.spm,
                'col_cent':self.col_cent,
                'row_cent':self.row_cent,
                'ticid':self.ticid}

        return EarlyTessLightCurve( time=self.time,
                                    flux=np.nansum(self.flux[:, aperture_mask], axis=1),
                                    flux_err=np.nansum(self.flux_err[:, aperture_mask]**2, axis=1)**0.5,
                                    **keys)

    @staticmethod
    def from_archive(target, cadence='long', quarter=None, month=None,
                     campaign=None, radius=1., targetlimit=1, verbose=True, **kwargs):
        """
        There's no archive yet!
        """
        raise ValueError("There's no TESS archive yet!")

    def __repr__(self):
        return('EarlyTessTPF Object (TIC{})'.format(self.ticid))

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
    def ticid(self):
        return self.header()['TIC_ID']

    @property
    def camera(self):
        return self.header()['CAM']

    @property
    def spm(self):
        return self.header()['SPM']

    @property
    def col_cent(self):
        return self.header()['COL_CENT']

    @property
    def row_cent(self):
        return self.header()['ROW_CENT']

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
        ax.set_title('TIC: {}'.format(self.ticid))


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
        factory.time = Time(gpstime, format='gps').jd
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
                                                   target_id=target_id)

        for idx, img in enumerate(images):

            # allow us to send hdu lists or filenames
            #if isinstance(img, fits.ImageHDU):
            #    hdu = img
            #el
            if isinstance(img, fits.HDUList):
                hdus = img
            else:
                hdus = fits.open(img)

            stamphdu = hdus[extension]
            framehdu = hdus[0]


            if idx == 0:  # Get default keyword values from the first image
                factory.keywords = hdu.header

            # add this cadence to the TOP
            factory.add_cadence(frameno=idx, flux=stamphdu.data, header=framehdu.header)

        return factory.get_tpf(**kwargs)

    @property
    def keplerid(self):
        return None

    def interact(self, lc=None):
        """
        (
        ZKBT -- made some tiny kludges to this to make it work.
        Long term, it'd be good to make it be a bit more mission
        agnostic, so it's easier to inherit from.
        )
        Display an interactive IPython Notebook widget to inspect the data.

        The widget will show both the lightcurve and pixel data.  By default,
        the lightcurve shown is obtained by calling the `to_lightcurve()` method,
        unless the user supplies a custom `LightCurve` object.

        Note: at this time, this feature only works inside an active Jupyter
        Notebook, and tends to be too slow when more than ~30,000 cadences
        are contained in the TPF (e.g. short cadence data).

        Parameters
        ----------
        lc : LightCurve object
            An optional pre-processed lightcurve object to show.
        """
        try:
            from ipywidgets import interact
            import ipywidgets as widgets
            from bokeh.io import push_notebook, show, output_notebook
            from bokeh.plotting import figure, ColumnDataSource
            from bokeh.models import Span, LogColorMapper
            from bokeh.layouts import row
            from bokeh.models.tools import HoverTool
            from IPython.display import display
            output_notebook()
        except ImportError:
            raise ImportError('The quicklook tool requires Bokeh and ipywidgets. '
                              'See the .interact() tutorial')

        ytitle = 'Flux'
        if lc is None:
            lc = self.to_lightcurve()
            ytitle = 'Flux (counts)'

        # Bokeh cannot handle many data points
        # https://github.com/bokeh/bokeh/issues/7490
        if len(lc.cadenceno) > 30000:
            raise RuntimeError('Interact cannot display more than 20000 cadences.')

        # Map cadence to index for quick array slicing.
        n_lc_cad = len(lc.cadenceno)
        n_cad, nx, ny = self.flux.shape
        lc_cad_matches = np.in1d(self.cadenceno, lc.cadenceno)
        if lc_cad_matches.sum() != n_lc_cad:
            raise ValueError("The lightcurve provided has cadences that are not "
                             "present in the Target Pixel File.")
        min_cadence, max_cadence = np.min(self.cadenceno), np.max(self.cadenceno)
        cadence_lookup = {cad: j for j, cad in enumerate(self.cadenceno)}
        cadence_full_range = np.arange(min_cadence, max_cadence, 1, dtype=np.int)
        missing_cadences = list(set(cadence_full_range)-set(self.cadenceno))

        # Convert binary quality numbers into human readable strings
        qual_strings = []
        for bitmask in lc.quality:
            flag_str_list = KeplerQualityFlags.decode(bitmask)
            if len(flag_str_list) == 0:
                qual_strings.append(' ')
            if len(flag_str_list) == 1:
                qual_strings.append(flag_str_list[0])
            if len(flag_str_list) > 1:
                qual_strings.append("; ".join(flag_str_list))

        # Convert time into human readable strings, breaks with NaN time
        # See https://github.com/KeplerGO/lightkurve/issues/116
        if (self.time == self.time).all():
            human_time = self.astropy_time.isot[lc_cad_matches]
        else:
            human_time = [' '] * n_lc_cad

        # Each data source will later become a hover-over tooltip
        source = ColumnDataSource(data=dict(
            time=lc.time,
            time_iso=human_time,
            flux=lc.flux,
            cadence=lc.cadenceno,
            quality_code=lc.quality,
            quality=np.array(qual_strings)))

        # Provide extra metadata in the title
        if self.mission == 'K2':
            title = "Quicklook lightcurve for EPIC {} (K2 Campaign {})".format(
                self.keplerid, self.campaign)
        elif self.mission == 'Kepler':
            title = "Quicklook lightcurve for KIC {} (Kepler Quarter {})".format(
                self.keplerid, self.quarter)
        elif self.mission == 'TESS':
            title = "Quicklook lightcurve for TIC{}".format(self.ticid)

        # Figure 1 shows the lightcurve with steps, tooltips, and vertical line
        fig1 = figure(title=title, plot_height=300, plot_width=600,
                      tools="pan,wheel_zoom,box_zoom,save,reset")
        fig1.yaxis.axis_label = ytitle
        fig1.xaxis.axis_label = 'Time (days)'
        fig1.step('time', 'flux', line_width=1, color='gray', source=source,
                  nonselection_line_color='gray', mode="center")

        r = fig1.circle('time', 'flux', source=source, fill_alpha=0.3, size=8,
                        line_color=None, selection_color="firebrick",
                        nonselection_fill_alpha=0.0, nonselection_line_color=None,
                        nonselection_line_alpha=0.0, fill_color=None,
                        hover_fill_color="firebrick", hover_alpha=0.9,
                        hover_line_color="white")

        fig1.add_tools(HoverTool(tooltips=[("Cadence", "@cadence"),
                                           ("Time (JD)", "@time{0,0.000}"),
                                           ("Time (ISO)", "@time_iso"),
                                           ("Flux", "@flux"),
                                           ("Quality Code", "@quality_code"),
                                           ("Quality Flag", "@quality")],
                                 renderers=[r],
                                 mode='mouse',
                                 point_policy="snap_to_data"))
        # Vertical line to indicate the cadence shown in Fig 2
        vert = Span(location=0, dimension='height', line_color='firebrick',
                    line_width=4, line_alpha=0.5)
        fig1.add_layout(vert)

        # Figure 2 shows the Target Pixel File stamp with log screen stretch
        fig2 = figure(plot_width=300, plot_height=300,
                      tools="pan,wheel_zoom,box_zoom,save,reset",
                      title='Pixel data | CAM{} | {}'.format(
                          self.camera, (self.col_cent, self.row_cent)))
        fig2.yaxis.axis_label = 'Pixel Row Number'
        fig2.xaxis.axis_label = 'Pixel Column Number'

        pedestal = np.nanmin(self.flux[lc_cad_matches, :, :])
        stretch_dims = np.prod(self.flux[lc_cad_matches, :, :].shape)
        screen_stretch = self.flux[lc_cad_matches, :, :].reshape(stretch_dims) - pedestal
        screen_stretch = screen_stretch[np.isfinite(screen_stretch)]  # ignore NaNs
        screen_stretch = screen_stretch[screen_stretch > 0.0]
        vlo = np.min(screen_stretch)
        vhi = np.max(screen_stretch)
        vstep = (np.log10(vhi) - np.log10(vlo)) / 300.0  # assumes counts >> 1.0!
        lo, med, hi = np.nanpercentile(screen_stretch, [1, 50, 95])
        color_mapper = LogColorMapper(palette="Viridis256", low=lo, high=hi)

        fig2_dat = fig2.image([self.flux[0, :, :] - pedestal], x=self.column,
                              y=self.row, dw=self.shape[2], dh=self.shape[1],
                              dilate=False, color_mapper=color_mapper)

        # The figures appear before the interactive widget sliders
        show(row(fig1, fig2), notebook_handle=True)

        # The widget sliders call the update function each time
        def update(cadence, log_stretch):
            """Function that connects to the interact widget slider values"""
            fig2_dat.glyph.color_mapper.high = 10**log_stretch[1]
            fig2_dat.glyph.color_mapper.low = 10**log_stretch[0]
            if cadence not in missing_cadences:
                index_val = cadence_lookup[cadence]
                vert.update(line_alpha=0.5)
                if self.time[index_val] == self.time[index_val]:
                    vert.update(location=self.time[index_val])
                else:
                    vert.update(line_alpha=0.0)
                fig2_dat.data_source.data['image'] = [self.flux[index_val, :, :]
                                                      - pedestal]
            else:
                vert.update(line_alpha=0)
                fig2_dat.data_source.data['image'] = [self.flux[0, :, :] * np.NaN]
            push_notebook()

        # Define the widgets that enable the interactivity
        play = widgets.Play(interval=10, value=min_cadence, min=min_cadence,
                            max=max_cadence, step=1, description="Press play",
                            disabled=False)
        play.show_repeat, play._repeat = False, False
        cadence_slider = widgets.IntSlider(
            min=min_cadence, max=max_cadence,
            step=1, value=min_cadence, description='Cadence',
            layout=widgets.Layout(width='40%', height='20px'))
        screen_slider = widgets.FloatRangeSlider(
            value=[np.log10(lo), np.log10(hi)],
            min=np.log10(vlo),
            max=np.log10(vhi),
            step=vstep,
            description='Pixel Stretch (log)',
            style={'description_width': 'initial'},
            continuous_update=False,
            layout=widgets.Layout(width='30%', height='20px'))
        widgets.jslink((play, 'value'), (cadence_slider, 'value'))
        ui = widgets.HBox([play, cadence_slider, screen_slider])
        out = widgets.interactive_output(update, {'cadence': cadence_slider,
                                                  'log_stretch': screen_slider})
        display(ui, out)


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
    def _make_primary_hdu(self, keywords={}):
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

    def _make_target_extension(self):
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
        cols.append(fits.Column(name='POS_CORR1', format='E', unit='pi xels',
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