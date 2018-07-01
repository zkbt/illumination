from ..imports import *
from ..postage import *
from .processing import *
from craftroom.oned import binto

def create_tpfs(s, stacker=Central(10), cadences=[2, 120,1800]):
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

def evaluate_strategy(tpf2s, directory='.', strategy=Central(10), cadence=1800, start=-np.inf, end=np.inf):
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

    Returns
    -------

    tpfs, lcs, summary
    '''

    # make the TPF
    tpfs = {}
    tpfs['raw'] = tpf2s
    s = Stamp(tpf2s)
    tpfs['crm'] = EarlyTessTargetPixelFile.from_stamp(s.stack(cadence, strategy=strategy))
    tpfs['nocrm'] = EarlyTessTargetPixelFile.from_stamp(s.stack(cadence, strategy=Sum()))

    # define the apertures for photometry and background subtraction
    aperture, backgroundaperture = define_apertures(tpfs['nocrm'])
    for k in tpfs.keys():
        # use the same aperture for all of them
        change_pipeline_aperture(tpfs[k], aperture, backgroundaperture)
        # subtract the background, redefining "flux" in each of these tpfs
        subtract_background(tpfs[k])



    lcs = {}
    lcs['raw'] = tpfs['raw'].to_lightcurve().normalize()

    for k in ['crm', 'nocrm']:
        lcs['{}-original'.format(k)] = tpfs[k].to_lightcurve().normalize()
        lcs['{}-flattened'.format(k)] = lcs['{}-original'.format(k)].remove_outliers().flatten()
        lcs['{}-corrected'.format(k)] = lcs['{}-original'.format(k)].remove_outliers().correct(polyorder=1, sigma_1=2.5, sigma_2=2.5)

    for k in lcs.keys():
        lc = lcs[k]

        # trim to time
        goodtime = (lc.time >= start)*(lc.time<=end)
        lcs[k] = lcs[k][goodtime]

        if k != 'raw':
            goodjitter = ok_jitter(lcs[k])
            lcs[k] = lcs[k][goodjitter]
        lcs[k] = lcs[k].normalize()

    '''
    jitter = {}
    jt, jc, jr, jce, jre = bin_jitter(lc, binwidth=lcs['nocrm'].cadence.to('day').value, robust=False)
    jitter['time'] = jt
    jitter['column'] = jc
    jitter['row'] = jr
    jitter['intraexposure'] = np.sqrt(jce**2 + jre**2)
    '''

    summary = {}
    summary['name'] = strategy.name
    for k in lcs.keys():
        if k == 'raw':
            continue
        lc = lcs[k]

        # calculate the RMS of each light curve
        summary['{}-madstd'.format(k, cadence/60)] = mad_std(lc.flux)
        summary['{}-std'.format(k, cadence/60)] = np.std(lc.flux)

        # calculate the equivalent for 30 minutes
        if cadence == 120:
            bx, by, bz = binto(lc.time, lc.flux, binwidth=0.5/24.0, robust=False, sem=True)
            summary['{}-madstd-30m'.format(k)] = mad_std(by)
            summary['{}-std-30m'.format(k)] = np.std(by)

        # calculate mad-std of binned differences
        for hours in [1, 3, 6, 9, 12]:
            bx, by, bz = binto(lc.time, lc.flux, binwidth=hours/24.0, robust=True)
            summary['{}-d{}hr-madstd'.format(k, hours)] = mad_std(np.diff(by))
            summary['{}-d{}hr-std'.format(k, hours)] = np.std(np.diff(by))

    summary['start'] = start
    summary['end'] = end

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

    # save the summary
    np.save(os.path.join(summary['directory'], 'summary.npy'), summary)

    # save the TPFs
    if subdirectory == 'entire':
        for k in tpfs.keys():
            if k != 'raw':
                tpfs[k].to_fits(directory=summary['directory'], zip=True)

    # save the light curves
    for k in ['crm', 'nocrm']:
        lc = lcs['{}-original'.format(k)]
        filename = os.path.join(summary['directory'], tpfs['crm'].filelabel() + '_' + k + '.csv')
        with open(filename, 'w') as f:
            f.write(lc.to_csv())

    return tpfs, lcs, summary
