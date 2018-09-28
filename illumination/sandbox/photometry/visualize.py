from ... import *
from ...imports import *

def plot_aperture_definition(tpf):
    '''
    For a given TPF, visualize its aperture definitions.
    '''

    aspect = tpf.shape[1]/float(tpf.shape[2])
    fi, ax = plt.subplots(1,3,figsize=(10, 1.8*aspect), sharex=True,sharey=True)
    frame = int(len(tpf.time)/2)
    tpf.plot(ax[0], frame=frame, bkg=True, clabel='')
    tpf.plot(ax[1], aperture_mask=tpf.hdu[-1].data == 2, frame=frame, bkg=True, clabel='')
    ax[1].set_title('background')
    tpf.plot(ax[2], aperture_mask=tpf.hdu[-1].data == 3, frame=frame, bkg=False, clabel='')
    ax[2].set_title('target')


def plot_histogram(y, bins=None, binwidth=0.1, ax=None, **kwargs):
    '''
    Plot a histogram, rotated clockwise by 90 degrees, to represent a projection of a timeseries plot.

    Parameters
    ----------

    y : array
        The y values to go into the histogram.

    bins : array
        The array of locations for the histogram (otherwise, requires binwidth)

    binwidth : float
        If bins aren't set, create a grid using this binwidth and the sample limits.

    ax : an Axes object
        (optional) Plot into a particular ax.

    **kwargs are passed to plt.plot()
    '''

    # create a histogram of the lightcurve values
    if bins is None:
        bins = np.arange(np.min(y)-binwidth, np.max(y)+binwidth, binwidth)

    ok = np.isfinite(y)
    yhist, edges = np.histogram(y[ok], bins=bins, density=True)

    # define the "x"-axis at the centers of the histogram bins
    xhist = (edges[1:] + edges[0:-1])/2.0
    binwidth = np.median(np.diff(xhist))

    # plot in the histogram panel
    if ax is None:
        ax = plt.gca()
    ax.plot(yhist, xhist, **kwargs)

    ax.set_xscale('log')
    ax.set_xlim(5.0/binwidth/len(y), 10*1.0/np.sqrt(2*np.pi)/binwidth)#np.max(yhist)*2)
    plt.axis('off')



def plot_timeseries(x, y, ax, ylim, ylabel='', color='black', alpha=1, **kw):
    '''
    Plot a single timeseries (with both 1D series and a collapsed histogram).
    '''
    try:
        plt.sca(ax[0])
    except IndexError:
        plt.sca(ax)
    # plot the timeseries
    plt.plot(x, y, color=color, alpha=alpha, **kw)

    # plot any outliers
    above = y > np.max(ylim)
    below = y < np.min(ylim)
    scale = 0.2*(np.max(ylim) - np.min(ylim))
    outlierkw = dict(**kw)
    outlierkw['alpha'] = 0.2
    outlierkw['elinewidth'] = 1
    outlierkw['linewidth'] = 0
    outlierkw['capsize'] = 0
    outlierkw['marker'] = None
    plt.errorbar(x[above], np.max(ylim)*np.ones_like(x[above]), scale, color=color, **outlierkw)
    plt.errorbar(x[below], np.min(ylim)*np.ones_like(x[below]), scale, color=color, **outlierkw)
    #plt.ylabel(ylabel)
    if np.isfinite(ylim).all():
        plt.ylim(*ylim)


    # plot the histogram
    try:
        plt.sca(ax[1])
        nbins = np.sqrt(len(y))
        plot_histogram(y, bins='auto', color=color, alpha=alpha) #bins=np.linspace(np.min(ylim), np.max(ylim), nbins)
        plt.ylim(*ylim)
    except IndexError:
        pass

def visualize_strategy(tpfs, lcs, summary, jitter, animation=False, nsigma=5, ylims={}, **kw):

    # create panels for the images we want to show
    i_nocrm = imshowFrame(data=tpfs['nocrm'], name='nocrm')
    i_nocrm.titlefordisplay = 'without CRM'

    i_crm = imshowFrame(data=tpfs['crm'], name='crm')
    i_crm.titlefordisplay = 'with CRM'

    diff = copy.deepcopy(tpfs['crm'])
    diff.hdu[1].data['FLUX'] = tpfs['nocrm'].raw_cnts - tpfs['crm'].raw_cnts
    i_diff = imshowFrame(data=diff, name='difference')
    i_diff.titlefordisplay = 'difference'

    i_aperture = imshowFrame(data=tpfs['crm'], name='aperture')
    i_aperture.titlefordisplay = '(aperture definition)'
    imshows = [i_nocrm, i_crm, i_diff, i_aperture]

    # create panels for timeseries to show
    timeseries = [EmptyTimeseriesFrame(name='original', ylabel='original\nflux', histogram=True),
                  EmptyTimeseriesFrame(name='flattened', ylabel='flattened\nflux', histogram=True),
                  EmptyTimeseriesFrame(name='corrected', ylabel='corrected\nflux', histogram=True),
                  EmptyTimeseriesFrame(name='fluxdiff', ylabel='CRM flux\ndifference', histogram=True),
                  EmptyTimeseriesFrame(name='column', ylabel='centroid\ncolumn\n(pix)', histogram=False),
                  EmptyTimeseriesFrame(name='row', ylabel='centroid\nrow\n(pix)', histogram=False),
                  EmptyTimeseriesFrame(name='intraexposure', ylabel='intra-\nexposure\njitter\n(pix)', histogram=False)]

    # put them all together
    i = GenericIllustration(imshows=imshows, timeseries=timeseries, sharecolorbar=False)
    i.plot()

    # add the aperture onto its imshow frame
    mask = tpfs['crm'].pipeline_mask == False
    extent = [0, mask.shape[1], 0, mask.shape[0]]
    i_aperture.ax.imshow(mask, interpolation='nearest', origin='lower', extent=extent, cmap=one2another(alphabottom=0, alphatop=0.5, top='purple'))
    i_aperture.ax.imshow(tpfs['crm'].background_mask, interpolation='nearest', origin='lower', extent=extent, cmap=one2another(alphabottom=0, alphatop=0.5, top='hotpink'))


    # plot the individual timeseries
    colors = dict(crm='mediumvioletred', nocrm='royalblue', raw='orange')
    lckw = dict(marker='.', markersize=8, linewidth=0, markeredgecolor='none')

    scale = nsigma*np.maximum(mad_std(lcs['crm-flattened'].flux),
                              mad_std(lcs['nocrm-flattened'].flux))

    for mode in ['original', 'flattened', 'corrected']:
        f = i.frames[mode]
        for c in ['nocrm', 'crm']:
            lc = lcs['{}-{}'.format(c, mode)]
            if mode in 'original':
                if mode in ylims:
                    ylim = ylims[mode]
                else:
                    bottom, top = np.nanpercentile(lc.flux, [1,99])
                    ylim = [np.minimum(bottom, 1-scale), np.maximum(top, 1+scale)]
            else:
                ylim = 1-scale, 1+scale
            plot_timeseries(lc.time - f.offset, lc.flux, [f.ax, f.ax_hist], ylim, color=colors[c], alpha=1, **lckw)

            f.ax_hist.text(0.995, 0.97 - (1.0 + 5*(c=='crm'))/7,
                              '{}: {}={:.0f}ppm, {}={:.0f}ppm, {}={:.0f}ppm'.format(
                                    c.upper(),
                                    r'$\sigma$', 1e6*summary['{}-{}-std-{:.0f}m'.format(c, mode, lc.cadence.to('min').value)],
                                    r'$\sigma_{clipped}$', 1e6*summary['{}-{}-clippedstd-{:.0f}m'.format(c, mode, lc.cadence.to('min').value)],
                                    r'$\sigma_{MAD}$', 1e6*summary['{}-{}-madstd-{:.0f}m'.format(c, mode, lc.cadence.to('min').value)]),
                              color=colors[c], ha='right', va='center', transform=f.ax.transAxes )

    # plot the centroid information
    centroid_scale = nsigma*np.maximum(mad_std(jitter['column']),mad_std(jitter['row']))
    centroid_ylim = [-centroid_scale, centroid_scale]
    for cen in ['column', 'row']:
        f = i.frames[cen]
        plot_timeseries(jitter['time']-f.offset, jitter[cen], [f.ax], centroid_ylim, color='dimgray', **lckw)

        for c in ['nocrm', 'crm']:
            lc = lcs['{}-original'.format(c)]
            if cen == 'column':
                y = lc.centroid_col
            elif cen == 'row':
                y = lc.centroid_row
            plot_timeseries(lc.time-f.offset, y-np.median(y), [f.ax], centroid_ylim, color=colors[c], alpha=0.5, **lckw)

    ylim =  [0, 2*nsigma*mad_std(jitter['intraexposure']) + np.median(jitter['intraexposure'])]
    f = i.frames['intraexposure']
    plot_timeseries(jitter['time']-f.offset, jitter['intraexposure'],  [f.ax], ylim, color='dimgray', **lckw)
    #f.ax.set_ylim(0, None)


    # calculate the net gains and losses
    lc_diff = {}
    normalization = tpfs['crm'].to_lightcurve().flux
    gains = copy.deepcopy(diff)
    gains.hdu[1].data['FLUX'] = np.maximum(gains.flux, 0)
    lc_diff['gains']  = gains.to_lightcurve().flux/normalization
    losses = copy.deepcopy(diff)
    losses.hdu[1].data['FLUX'] = np.minimum(losses.flux, 0)
    lc_diff['losses'] = losses.to_lightcurve().flux/normalization

    #lc_diff['net'] = lc_diff['gains'] + lc_diff['losses']
    colors_diff = dict(gains='royalblue', losses='firebrick', net='dimgray')
    f = i.frames['fluxdiff']
    t = gains.time - f.offset
    scale = 2*nsigma*mad_std(lc_diff['gains'] + lc_diff['losses'])
    ylim = [-scale, scale]
    for k, l in lc_diff.items():
        plot_timeseries(t, l,
                        ax=[f.ax, f.ax_hist],
                        ylim=ylim,
                        color=colors_diff[k],
                        linewidth=1, alpha=0.5)
    plot_timeseries(t, lc_diff['gains'] + lc_diff['losses'],
                    ax=[f.ax, f.ax_hist],
                    ylim=ylim,
                    color='dimgray',
                    **lckw)
    for a in [f.ax, f.ax_hist]:
        a.axhline(0, color='gray', alpha=0.3)

    title = ' | '.join([imshows[0].data.titlefordisplay.replace('\n', ' | '), summary['name'], '{:.2g} DN/s'.format(summary['medflux'])])
    plt.suptitle(title, fontsize=20)

    for t in timeseries:
        try:
            t.ax.set_xlim(summary['start'] - t.offset, summary['end'] - t.offset)
        except (ValueError, TypeError):
            pass

    d = summary['directory']
    filename = 'tic{}_{:.0f}m_{}'.format(tpfs['crm'].tic_id, tpfs['crm'].cadence.to('minute').value, summary['name'].replace(' ',''))
    plt.savefig(os.path.join(d, filename+'.pdf'))
    if animation:
        i.animate(cadence=tpfs['crm'].cadence, filename=os.path.join(d, filename+'.mp4'), mintime=Time(summary['start'], format='jd', scale='tdb'), maxtimespan=(summary['end'] - summary['start'])*u.day, **kw)
    return i



def plot_jitter_correlate(path):
    '''
    Make and save a jitter correlation plot for a given directory path
    (that must contain some light curves, a jitter, and a summary).
    '''
    label = path.split('/')[-3].replace('_', ' | ')
    lcfiles = glob.glob(os.path.join(path, '*.csv'))
    lcs = {}
    for f in lcfiles:
        k = f.split('_')[-1].split('.csv')[0]
        lcs[k] = ascii.read(f, delimiter=',', data_start=1, names='time,time1,flux,flux_err,quality,centroid_col,centroid_row'.split(','))
    diff = lcs['nocrm']['flux'] - lcs['crm']['flux']

    jitterfile = os.path.join(path, 'jitter.npy')
    jitter = np.load(jitterfile, encoding='latin1')[()]


    summaryfile = os.path.join(path, 'summary.npy')
    summary = np.load(summaryfile, encoding='latin1')[()]

    rows = dict(crm=lcs['crm']['flux'], nocrm=lcs['nocrm']['flux'])
    rows['nocrm-crm'] = diff
    # make a plot
    fi, ax = plt.subplots(3, 4, sharey='row', sharex='col', figsize=(10, 7), dpi=200,
                         gridspec_kw=dict(hspace=0.04, wspace=0.04))
    for row, ylabel in enumerate(['nocrm', 'crm', 'nocrm-crm']):
        for col, k in enumerate(['row', 'column', 'intraexposure', 'time']):
            plt.sca(ax[row, col])
            x = jitter[k][:len(diff)]
            if k == 'time':
                x-= np.min(x)
            y = rows[ylabel]

            xlim = np.nanpercentile(x[np.isfinite(x)], [2, 98])
            ylim = np.nanpercentile(y[np.isfinite(y)], [2, 98])
            plt.plot(x, y, '.', alpha=0.5, markeredgecolor='none', color='mediumseagreen')

            ok = (x >= xlim[0])*(x <= xlim[1])*(y >= ylim[0])*(y <= ylim[1])
            nbins=20
            bx, by, be = binto(x[ok], y[ok], binwidth=(xlim[1] - xlim[0])/nbins, robust=True)
            plt.errorbar(bx, by, be, color='black', linewidth=0, elinewidth=4, zorder=10)


            plt.axhline(0, color='black', zorder=100, alpha=0.5)
            if col == 0:
                plt.ylabel(ylabel)#('Fractional flux\nlost to CRM')
            if row == 2:
                plt.xlabel(k)

            rho = scipy.stats.spearmanr(x[ok],y[ok])[0]
            R = scipy.stats.pearsonr(x[ok],y[ok])[0]
            plt.text(0.05, 0.95, 'R={:.3f}\n{}={:.3f}'.format(R, r'$\rho$', rho), transform=plt.gca().transAxes, ha='left', va='top')
            if k != 'intraexposure' or ylabel != 'nocrm-crm':
                plt.gca().set_facecolor('gainsboro')

            plt.xlim(*xlim)
            plt.ylim(*ylim)
    plt.suptitle(summary['title'].replace('s |', 's\n') + ' | {:.2g} DN/s'.format(summary['medflux']))
    #plt.tight_layout()
    filename = 'jitter_' + summary['title'].replace(' | ', '_').replace(' ', '') + '.pdf'
    plt.savefig(os.path.join(path, filename))
    print(os.path.join(path, filename))
