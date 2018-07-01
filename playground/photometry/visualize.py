from ..tv import *
from ..imports import *

def plot_aperture_definition(tpf):
    fi, ax = plt.subplots(1,3,figsize=(10, 2), sharex=True,sharey=True)
    frame = int(len(tpf.time)/2)
    tpf.plot(ax[0], frame=frame, bkg=True, clabel='')
    tpf.plot(ax[1], aperture_mask=tpf.hdu[-1].data == 2, frame=frame, bkg=True, clabel='')
    ax[1].set_title('background')
    tpf.plot(ax[2], aperture_mask=tpf.hdu[-1].data == 3, frame=frame, bkg=False, clabel='')
    ax[2].set_title('target')



def animate_temporal_differences(tpf, maxtimespan=0.02*u.day, cadence=None,sharecolorbar=False, **kw):
    diff = tpf.differences()
    i = StampsIllustration([tpf, diff], sharecolorbar=sharecolorbar)
    i.plot()
    animate(i, maxtimespan=maxtimespan, cadence=cadence, **kw)

def animate_both_cadences(tpfs, filename='both_cadences.mp4', maxtimespan=30*u.minute, **kw):

    raw = tpfs['raw']
    crm = tpfs['crm']
    nocrm = tpfs['nocrm']

    i = StampsIllustration([raw, crm, nocrm], names=['raw', 'CRM', 'no CRM'], sharecolorbar=False)
    for k, f in i.frames.items():
        f.titlefordisplay = '{}\n{}'.format(k, f.titlefordisplay)
    i.plot()

    animate(i, cadence=raw.cadence, maxtimespan=maxtimespan, filename=filename, **kw)


def animate_cosmics(tpfs, filename='mitigated_cosmics.mp4', maxtimespan=0.25*u.day, **kw):

    crm = tpfs['crm']
    nocrm = tpfs['nocrm']

    diff = copy.deepcopy(crm)
    diff.hdu[1].data['FLUX'] = nocrm.raw_cnts - crm.raw_cnts
    i = StampsIllustration([crm, nocrm, diff], names=['CRM', 'no CRM', 'difference'], sharecolorbar=False)
    for k, f in i.frames.items():
        f.titlefordisplay = '{}\n{}'.format(k, f.titlefordisplay)
    i.plot()
    animate(i, cadence=crm.cadence, maxtimespan=maxtimespan, filename=filename, **kw)


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
    else:
        binwidth = np.median(np.diff(bins))

    ok = np.isfinite(y)
    yhist, edges = np.histogram(y[ok], bins=bins, density=True)

    # define the "x"-axis at the centers of the histogram bins
    xhist = (edges[1:] + edges[0:-1])/2.0

    # plot in the histogram panel
    if ax is None:
        ax = plt.gca()
    ax.plot(yhist, xhist, **kwargs)

    ax.set_xscale('log')
    ax.set_xlim(1.9/binwidth/len(y), 100*1.0/np.sqrt(2*np.pi)/binwidth)#np.max(yhist)*2)
    plt.axis('off')


def bin_jitter(lc, binwidth=30.0/60./24, robust=False):

    c, r = lc.centroid_col, lc.centroid_row

    #bx, by, be = binto(lc.time, np.sqrt(c**2 + r**2), binwidth=binwidth, sem=False, robust=True)
    #plt.bar(bx, be, width=binwidth, alpha=0.3, label='radial')

    time, ry, re = binto(lc.time, r, binwidth=binwidth, sem=False, robust=False)
    _, cy, ce = binto(lc.time, c, binwidth=binwidth, sem=False, robust=False)


    centroid_col = cy - np.nanmedian(cy)
    centroid_row = ry - np.nanmedian(ry)
    intrajitter_col = ce
    intrajitter_row = re
    return time, centroid_col, centroid_row, intrajitter_col, intrajitter_row

def plot_timeseries(x, y, ax, ylim, ylabel='', color='black', **kw):
    '''
    Plot a timeseries (with both 1D series and a collapsed histogram).
    '''
    plt.sca(ax[0])
    # plot the timeseries
    plt.plot(x, y, color=color, **kw)

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
    plt.errorbar(x[below], np.max(ylim)*np.ones_like(x[below]), scale, color=color, **outlierkw)
    plt.ylabel(ylabel)
    plt.ylim(*ylim)


    # plot the histogram
    plt.sca(ax[1])
    nbins = np.sqrt(len(y))
    plot_histogram(y, bins=np.linspace(np.min(ylim), np.max(ylim), nbins), color=color)
    plt.ylim(*ylim)

def plot_lcs(lcs, summary, xlim=[None, None], title='', nsigma=5):

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
                              '{}\n{:.0f}ppm'.format(k.upper(), 1e6*summary['{}-{}-madstd'.format(k, mode)]),
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

def visualize_strategy(tpfs, lcs, summary, animation=True, **kw):
    d = summary['directory']
    mkdir(d)

    plot_lcs(lcs, summary, title=summary['title'], **kw)
    plt.savefig(os.path.join(d, 'lightcurves.pdf'))

    plot_aperture_definition(tpfs['nocrm'])
    plt.savefig(os.path.join(d, 'apertures.pdf'))

    if animation:
        animate_cosmics(tpfs, maxtimespan=6*u.hour, filename=os.path.join(d, 'mitigated_cosmics.mp4'), **kw)
        #animate_both_cadences(tpfs, maxtimespan=10*u.minute, filename=os.path.join(d, 'both_cadences.mp4'), **kw)
