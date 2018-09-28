from ...imports import *
from ...postage import *
from .processing import *


def create_tpfs(s, stacker=Central(10), cadences=[2, 120,1800]):
    '''
    Starting from a Stamp, create stacked tpfs at multiple cadences.
    '''


    tpfs = {c:{} for c in cadences + [2]}
    tpfs[2]['raw'] = EarlyTessTargetPixelFile.from_stamp(s)
    for cadence in cadences:
        try:
            tpfs[cadence]['crm'] = EarlyTessTargetPixelFile.from_stamp(s.stack(cadence, strategy=stacker))
        except ValueError:
            pass
        tpfs[cadence]['nocrm'] = EarlyTessTargetPixelFile.from_stamp(s.stack(cadence, strategy=Sum()))
    return tpfs


def ok_jitter(lc, threshold=0.15, visualize=False):
    '''
    Create a mask of where the jitter is OK-ish.
    '''
    def off(x):
        return (x-np.median(x))

    ok = np.sqrt(off(lc.centroid_col)**2 + off(lc.centroid_row)**2) < threshold
    if visualize:
        fi, ax = plt.subplots(2, 1)
        for row, y in enumerate([lc.centroid_col, lc.centroid_row]):
            for which in [ok, ~ok]:
                ax[row].scatter(lc[which].time, y[which])
        ax[0].set_ylabel('col (pix)'); ax[1].set_ylabel('row (pix)')

    return ok

def save(tpfs, lcs, summary, jitter, directory):

    # save the summary
    np.save(os.path.join(directory, 'summary.npy'), summary)

    # save the jitter
    np.save(os.path.join(directory, 'jitter.npy'), jitter)

    # save the TPFs
    #if subdirectory == 'entire':
    for k in tpfs.keys():
        if k != 'raw':
            tpfs[k].to_fits(output_fn=os.path.join(directory, '{}_{}.fits'.format(tpfs[k].filelabel(), k)), zip=True)

    # save the light curves
    for k in ['crm', 'nocrm']:
        lc = lcs['{}-original'.format(k)]
        filename = os.path.join(directory, tpfs['crm'].filelabel() + '_' + k + '.csv')
        with open(filename, 'w') as f:
            f.write(lc.to_csv())

def make_tpfs(tpf2s, strategy=Central(10), cadence=1800):

    # create a stamp, for stacking into new TPFs
    s = Stamp(tpf2s)
    crm = EarlyTessTargetPixelFile.from_stamp(s.stack(cadence, strategy=strategy))
    nocrm = EarlyTessTargetPixelFile.from_stamp(s.stack(cadence, strategy=Sum()))

    return crm, nocrm


def evaluate_strategy(tpf2s,
                      directory='.',
                      strategy=Central(10),
                      cadence=1800,
                      start=-np.inf, end=np.inf,
                      aperturekw={},
                      flattenkw={},
                      correctkw={},
                      flattentimescale=0.25,
                      ):
    '''
    Evaluate a cosmic ray mitigation strategy on a TPF.

    Parameters
    ----------

    tpf2s : a TargetPixelFile object
        This is a TPF, ideally of a fairly isolated star.
        It should be at 2s cadence.

    strategy : a Stacker object
        The strategy to be used for mitigating cosmic rays.
        It defaults to a Central 8/10 strategy.

    cadence : int
        The cadence on which to evaluate the performance.

    start : float
        Minimum time to include (JD)

    end : float
        Maximum time to include (JD)

    flattentimescale : float
        The window size for the SG filter in flatten,
        expressed in days. This will be converted to
        the closest odd integer number of cadences.

    flattenkw : dict
        keyword arguments for .flatten()

    correctkw : dict
        keyword arguments for .correct()

    aperturekw : dict
        keyword arguments for define_apertures

    flattenkw : dict

    Returns
    -------

    tpfs : dict
        'crm' and 'nocrm' TPFs
    lcs : dict
        'crm' and 'nocrm' light curves with various processing
    summary : dict
        Summary of noise properties.
    jitter : dict
        a jitter timeseries
    '''
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')

        # make the TPFs
        tpfs = {}
        tpfs['raw'] = tpf2s

        # create a stamp, for stacking into new TPFs
        s = Stamp(tpf2s)
        tpfs['crm'], tpfs['nocrm'] = make_tpfs(tpf2s, strategy=strategy)

        # define the apertures for photometry and background subtraction
        aperture, backgroundaperture = define_apertures(tpfs['nocrm'], **aperturekw)
        for k in tpfs.keys():

            # use the same aperture for all of them
            change_pipeline_aperture(tpfs[k], aperture, backgroundaperture)

            # subtract the background, redefining "flux" in each of these tpfs
            subtract_background(tpfs[k])



        # create light curve from the raw 2-s cadence
        raw = tpfs['raw'].to_lightcurve()

        # keep track of some summary statistics
        summary = {}
        summary['medflux'] = np.median(raw.flux)/raw.cadence.to('s').value

        ########################
        # KLUDGE (for bright stars)
        if (summary['medflux'] > 5e4) and 'apertureradius' not in aperturekw:
            # define the apertures for photometry and background subtraction
            aperturekw['apertureradius'] = 5 + np.sqrt(summary['medflux']/5e4)
            aperture, backgroundaperture = define_apertures(tpfs['nocrm'], **aperturekw)
            for k in tpfs.keys():

                # use the same aperture for all of them
                change_pipeline_aperture(tpfs[k], aperture, backgroundaperture)

                # subtract the background, redefining "flux" in each of these tpfs
                subtract_background(tpfs[k])

            # create light curve from the raw 2-s cadence
            raw = tpfs['raw'].to_lightcurve()

            # keep track of some summary statistics
            summary = {}
            summary['medflux'] = np.median(raw.flux)/raw.cadence.to('s').value

        lcs = {}
        lcs['raw'] = raw.normalize()

        # figure out an appropriate flatten window_length
        flattenkw['window_length'] = int(np.round(flattentimescale*24.0*3600.0/cadence))
        if (flattenkw['window_length'] % 2) == 0:
            flattenkw['window_length'] += 1
        correctkw['restore_trend'] = True

        # create all kinds of lightcurves
        for k in ['crm', 'nocrm']:

            # make a basic light curve
            lcs['{}-original'.format(k)] = tpfs[k].to_lightcurve().normalize()

            # flatten the light curve by removing temporal trends
            try:
                lcs['{}-flattened'.format(k)] = lcs['{}-original'.format(k)].remove_outliers().flatten(**flattenkw)
            except:
                print("{}-flattened lightcurve couldn't be made".format(k))
                lcs['{}-flattened'.format(k)] = lcs['{}-original'.format(k)].remove_outliers()

            # attempt to correct the light curve using SFF
            try:
                lcs['{}-corrected'.format(k)] = lcs['{}-original'.format(k)].remove_outliers().correct(**correctkw).flatten(**flattenkw)
            except:
                print("{}-corrected lightcurve couldn't be made".format(k))
                lcs['{}-corrected'.format(k)] = lcs['{}-flattened'.format(k)]

        # trim this timespan
        for k in lcs.keys():
            lc = lcs[k]

            # trim to time
            goodtime = (lc.time >= start)*(lc.time<=end)
            lcs[k] = lcs[k][goodtime]

        # record the jitter
        jitter = {}
        jt, jc, jr, jce, jre = bin_jitter(lcs['raw'], binwidth=(cadence*u.s/u.day).decompose(), robust=False)
        jitter['time'] = jt
        jitter['column'] = jc
        jitter['row'] = jr
        jitter['intraexposure'] = np.sqrt(jce**2 + jre**2)


        summary['name'] = strategy.name
        summary['ntotal'] = len(lcs['crm-original'].flux)
        for k in lcs.keys():
            if k == 'raw':
                continue
            lc = lcs[k]


            # mark the bad jitter moments
            badjitter = ok_jitter(lc) == False
            lc.quality = lc.quality | (4*badjitter)

            #    goodjitter = np.ones_like(lc.flux).astype(np.bool)
            #    lcs[k] = lcs[k][goodjitter]

            # calculate the RMS of each light curve
            ok = lc.quality == 0
            summary['{}-madstd-{:.0f}m'.format(k, cadence/60)] = mad_std(lc.flux[ok])
            summary['{}-std-{:.0f}m'.format(k, cadence/60)] = np.std(lc.flux[ok])
            clipped = sigma_clip(lc.flux[ok], sigma=3)
            fnotclipped = 1- np.sum(clipped.mask)/summary['ntotal']
            summary['{}-fractionnotclipped-{:.0f}m'.format(k, cadence/60)] = fnotclipped
            summary['{}-clippedstd-{:.0f}m'.format(k, cadence/60)] = np.std(clipped)/np.sqrt(fnotclipped)

            # calculate the equivalent for 30 minutes
            if cadence == 120:
                bx, by, bz = binto(lc.time[ok], lc.flux[ok], binwidth=0.5/24.0, robust=False, sem=True)
                summary['{}-madstd-30m'.format(k)] = mad_std(by)
                summary['{}-std-30m'.format(k)] = np.std(by)
                clipped = sigma_clip(by, sigma=3)
                fnotclipped = 1 - np.sum(clipped.mask)/summary['ntotal']
                summary['{}-fractionnotclipped-30m'.format(k)] = fnotclipped
                summary['{}-clippedstd-30m'.format(k)] = np.std(clipped)/np.sqrt(fnotclipped)

            # calculate mad-std of binned differences
            for hours in [1, 3, 6, 9, 12]:
                bx, by, bz = binto(lc.time[ok], lc.flux[ok], binwidth=hours/24.0, robust=True)
                summary['{}-d{}hr-madstd'.format(k, hours)] = mad_std(np.diff(by))
                summary['{}-d{}hr-std'.format(k, hours)] = np.std(np.diff(by))
                clipped = sigma_clip(np.diff(by), sigma=3)
                fnotclipped = 1 - np.sum(clipped.mask)/summary['ntotal']
                summary['{}-d{}hr-clippedstd'.format(k, hours)] = np.std(clipped)/np.sqrt(fnotclipped)

        if np.isfinite(start):
            summary['start'] = start
        else:
            summary['start'] = np.min(lcs['raw'].time)

        if np.isfinite(end):
            summary['end'] = end
        else:
            summary['end'] = np.max(lcs['raw'].time)
        summary['title'] = tpfs['crm'].filelabel().replace('_', ' | ') + ' | ' + strategy.name


        if np.isfinite(start) or np.isfinite(end):
            summary['title'] += ' | {:.5f} to {:.5f}'.format(start, end)

        # make sure the directories exist
        summary['directory'] = os.path.join(directory, strategy.name.replace(' ', ''))
        mkdir(summary['directory'])
        summary['directory'] = os.path.join(summary['directory'], tpfs['crm'].filelabel())
        mkdir(summary['directory'])
        if np.isfinite(start) or np.isfinite(end):
            subdirectory = '{:.5f}to{:.5f}'.format(start, end)
        else:
            subdirectory = 'entire'
        summary['directory'] = os.path.join(summary['directory'], subdirectory)
        mkdir(summary['directory'])

        # save everything
        save(tpfs, lcs, summary, jitter, directory=summary['directory'])

        return tpfs, lcs, summary, jitter
