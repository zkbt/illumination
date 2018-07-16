from ..tv import *
from ..imports import *

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
    plt.ylim(*ylim)


    # plot the histogram
    try:
        plt.sca(ax[1])
        nbins = np.sqrt(len(y))
        plot_histogram(y, bins='auto', color=color, alpha=alpha) #bins=np.linspace(np.min(ylim), np.max(ylim), nbins)
        plt.ylim(*ylim)
    except IndexError:
        pass

def plot_lcs(lcs, summary, xlim=[None, None], title='', nsigma=5):
    '''
    Make a comprehensive plot of LCs.
    '''

    # set up basic geometry
    N_lc = 3
    N_other = 3
    fi, ax = plt.subplots(N_lc + N_other, 2, figsize=(15, 10), sharey='row', sharex='col',
                          gridspec_kw=dict(hspace=0.1, wspace=0.0,
                                           width_ratios=[1, 0.2],
                                           height_ratios=[2]*N_lc+[2]*N_other))

    # set up the basic plotting defaults
    colors = dict(crm='mediumvioletred', nocrm='royalblue', raw='orange')
    lckw = dict(alpha=0.5, marker='o', linewidth=0, markeredgecolor='none')

    # set the yscale for plotting light curves
    scale = nsigma*np.maximum(mad_std(lcs['crm-flattened'].flux),
                              mad_std(lcs['nocrm-flattened'].flux))
    ylim = 1-scale, 1+scale


    #for k in lcs.keys():
    #    lcs[k].time -= timeoffset
    #    lcs[k] = lcs[k][lcs[k].time < xspan]
    o = np.min(lcs['raw'].time)

    for k in ['nocrm', 'crm']:
        for i, mode in enumerate(['original', 'flattened', 'corrected']):
            lc = lcs['{}-{}'.format(k, mode)]
            plot_timeseries(lc.time-o, lc.flux, ax[i], ylim, ylabel=mode, color=colors[k], **lckw)
            ax[i, 1].text(0.8, 1 - (1.0 + (k=='crm'))/3,
                          '{}\n{:.0f}ppm'.format(k.upper(), 1e6*summary['{}-{}-madstd-{:.0f}m'.format(k, mode, lc.cadence.to('min').value)]),
                          transform=ax[i,1].transAxes, color=colors[k],
                          ha='left', va='center')

    lc = lcs['raw']
    jt, jc, jr, jce, jre = bin_jitter(lc, binwidth=lcs['nocrm-original'].cadence.to('day').value, robust=False)
    centroid_scale = nsigma*np.maximum(mad_std(jc), mad_std(jr))
    centroid_ylim = [-0.106, 0.106]#[-centroid_scale, centroid_scale]
    plot_timeseries(jt-o, jc, ax[3], centroid_ylim, color='black', **lckw)
    plot_timeseries(jt-o, jr, ax[4], centroid_ylim, color='black', **lckw)

    for k in ['nocrm', 'crm']:
        lc = lcs['{}-original'.format(k)]
        plot_timeseries(lc.time-o, lc.centroid_col - np.median(lc.centroid_col), ax[3], centroid_ylim,  ylabel='column\n(pix)', color=colors[k], **lckw)
        plot_timeseries(lc.time-o, lc.centroid_row - np.median(lc.centroid_row), ax[4], centroid_ylim,  ylabel='row\n(pix)', color=colors[k], **lckw)

    plt.sca(ax[3,1])
    plt.text(0.8, 0.5, '$\sigma=$\n{:.3f}px'.format(mad_std(jc)),
                 transform=plt.gca().transAxes, color='black', alpha=0.5,
                 ha='left', va='center')

    plt.sca(ax[4,1])
    plt.text(0.8, 0.5, '$\sigma=$\n{:.3f}px'.format(mad_std(jr)),
                 transform=plt.gca().transAxes, color='black', alpha=0.5,
                 ha='left', va='center')

    plot_timeseries(jt-o, np.sqrt(jce**2 + jre**2), ax[5], [0, 0.5],  ylabel='intra-\nexposure\njitter (pix)', color='black', **lckw)
    plt.sca(ax[5,1])
    plt.text(0.8, 0.5, 'avg=\n{:.3f}px'.format(np.mean(np.sqrt(jce**2 + jre**2))),
                 transform=plt.gca().transAxes, color='black', alpha=0.5,
                 ha='left', va='center')

    ax[0,0].set_xlim(*xlim)
    ax[0,0].set_title(title)
    ax[-1,0].set_xlabel('Time - {:.5f} (days)'.format(o))


def visualize_strategy(tpfs, lcs, summary, jitter, animation=False, nsigma=5, **kw):

    # create panels for the images we want to show
    i_nocrm = imshowFrame(data=tpfs['nocrm'], name='nocrm')
    i_nocrm.titlefordisplay = 'without CRM'

    i_crm = imshowFrame(data=tpfs['crm'], name='crm')
    i_crm.titlefordisplay = 'with CRM'

    diff = copy.deepcopy(tpfs['crm'])
    diff.hdu[1].data['FLUX'] = tpfs['nocrm'].flux - tpfs['crm'].flux
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
    i = HybridIllustration(imshows=imshows, timeseries=timeseries, sharecolorbar=False)
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
    ylim = 1-scale, 1+scale

    for mode in ['original', 'flattened', 'corrected']:
        f = i.frames[mode]
        for c in ['nocrm', 'crm']:
            lc = lcs['{}-{}'.format(c, mode)]
            plot_timeseries(lc.time - f.offset, lc.flux, [f.ax, f.ax_hist], ylim, color=colors[c], alpha=1, **lckw)
            f.ax_hist.text(0.995, 1 - (1.0 + 5*(c=='crm'))/7,
                              '{}: {:.0f}ppm'.format(c.upper(), 1e6*summary['{}-{}-madstd-{:.0f}m'.format(c, mode, lc.cadence.to('min').value)]),
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

    ylim =  [0, nsigma*mad_std(jitter['intraexposure']) + np.median(jitter['intraexposure'])]
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
    ylim = [np.percentile(lc_diff['losses'], 1), np.percentile(lc_diff['gains'], 99)]
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
        animate(i, cadence=tpfs['crm'].cadence, filename=os.path.join(d, filename+'.mp4'), mintime=Time(summary['start'], format='jd', scale='tdb'), maxtimespan=(summary['end'] - summary['start'])*u.day, **kw)
    return i
