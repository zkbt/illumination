from .visualize import *

def animate_temporal_differences(tpf, maxtimespan=0.02*u.day, cadence=None, sharecolorbar=False, **kw):
    '''
    For a given TPF, animate its temporal differences.
    '''

    # createa a TPF of temporal differences
    diff = tpf.differences()

    # create an illustration the original and the difference
    i = StampsIllustration([tpf, diff], sharecolorbar=sharecolorbar)
    i.plot()

    if cadence is None:
        cadence = tpf.cadence

    # animate the
    i.animate(maxtimespan=maxtimespan, cadence=cadence, **kw)

def animate_both_cadences(tpfs, filename='both_cadences.mp4', maxtimespan=30*u.minute, **kw):
    '''
    For a dictionary of TPFS, animate both the raw and the stacked images.
    '''

    raw = tpfs['raw']
    crm = tpfs['crm']
    nocrm = tpfs['nocrm']

    i = StampsIllustration([raw, crm, nocrm], names=['raw', 'CRM', 'no CRM'], sharecolorbar=False)
    for k, f in i.frames.items():
        f.titlefordisplay = '{}\n{}'.format(k, f.titlefordisplay)
    i.plot()

    i.animate(cadence=raw.cadence, maxtimespan=maxtimespan, filename=filename, **kw)


def animate_cosmics(tpfs, filename='mitigated_cosmics.mp4', maxtimespan=0.25*u.day, **kw):
    '''
    For a dictionary of TPFs, animate the mitigated cosmic rays.
    '''

    crm = tpfs['crm']
    nocrm = tpfs['nocrm']

    # make a difference TPF
    diff = copy.deepcopy(crm)
    diff.hdu[1].data['FLUX'] = nocrm.raw_cnts - crm.raw_cnts
    i = StampsIllustration([crm, nocrm, diff], names=['CRM', 'no CRM', 'difference'], sharecolorbar=False)
    for k, f in i.frames.items():
        f.titlefordisplay = '{}\n{}'.format(k, f.titlefordisplay)
    i.plot()
    i.animate(cadence=crm.cadence, maxtimespan=maxtimespan, filename=filename, **kw)
