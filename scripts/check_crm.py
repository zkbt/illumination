#tic = 248093171
from playground.cosmics.stamps import *
from playground.tv.illustrations import CubesIllustration

possible = glob.glob('/pdo/ramp/zkbt/orbit-8193/stamps/spm*/tic*_*_cam*_spm*_*s.npy')
tics = [int(f.split('tic')[1].split('_')[0]) for f in possible]

#for tic in tics:

def checkcrm(tic=tics[0]):

    stamps = {}
    kinds = ['2s', 'nocrm', 'crm']
    for spm, name in zip([1,2,3], kinds):
        search = '/pdo/ramp/zkbt/orbit-8193/stamps/spm*/tic{}_*_cam*_spm{}_*s.npy'.format(tic, spm)
        file = glob.glob(search)[0]
        stamps[name] = Stamp(file)

    stamps['difference'] = copy.copy(stamps['nocrm'])
    stamps['difference'].photons = stamps['nocrm'].photons - stamps['crm'].photons*5/4
    stamps['difference'].consider()

    #stamps['zach'] = stamps['2s'].stack(120)
    #stamps['zach'].titlefordisplay = 'Zach'
    #def bla(x):
    #    return ''
    #stamps['zach'].colorbarlabelfordisplay = bla

    #stamps['zachdifference'] = copy.copy(stamps['nocrm'])
    #stamps['zachdifference'].photons = stamps['zach'].photons - stamps['onboardcrm'].photons*5/4
    #stamps['zachdifference'].consider()

    # imshow


    todisplay = ['2s', 'nocrm', 'crm', 'difference']
    ci = CubesIllustration([stamps[k] for k in todisplay], names=todisplay)
    ci.plot()

    '''
    fi, ax = plt.subplots(1, len(stamps), sharex=True, sharey=True, figsize=(20,6), dpi=50)
    for i, k in enumerate(kinds):# + ['difference'] + ['zach']):
        plt.sca(ax[i])
        stamps[k].imshow()

    # plots
    plt.figure()
    for k in stamps.keys():
        t = stamps[k].time
        f = stamps[k].photons.sum(-1).sum(-1)
        plt.scatter(t, f/stamps[k].cadence, s=2, label=k)
    '''
    return stamps, ci
