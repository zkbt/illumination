#tic = 248093171
from playground.tpf.stamps import *
from playground.tv.illustrations import StampsIllustration
from playground.tv.animation import animate

path = '/pdo/ramp/zkbt/orbit-8196/stamps'
possible = glob.glob(os.path.join(path, '/cam*/*.npy'))
tics = [int(f.split('tic')[1].split('_')[0]) for f in possible]

#for tic in tics:

def check_crm(tic=tics[0], movie=False, mintime = 1209031557, maxtimespan=600):
    '''
    For a give TIC, this loads a pre-created .npy stamp
    and extracts the appropriate 2s, 120s with CRM, and 120s no CRM
    data for each.
    '''

    stamps = {}
    kinds = ['2s', 'nocrm', 'crm']
    for spm, name in zip([1,2,3], kinds):
        search = '/pdo/ramp/zkbt/orbit-8193/stamps/spm*/tic{}_*_cam*_spm{}_*s.npy'.format(tic, spm)
        file = glob.glob(search)[0]
        stamps[name] = Stamp(file)

    stamps['2s'].label = '2s'
    stamps['nocrm'].label = '120s | No CRM'
    stamps['crm'].label = '120s | CRM'
    stamps['difference'] = copy.copy(stamps['nocrm'])
    stamps['difference'].photons = stamps['nocrm'].photons - stamps['crm'].photons*5/4
    stamps['difference'].consider()
    stamps['difference'].label = '120s | (No CRM) - (CRM)*10/8'

    basedirectory = '/pdo/ramp/zkbt/orbit-8193/stamps/'
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
    ci = StampsIllustration([stamps[k] for k in todisplay], names=todisplay)
    ci.plot()

    if movie:
        animate(ci, mintime=mintime, maxtimespan=maxtimespan, filename=os.path.join(basedirectory, '{}-crm.mp4'.format(tic)))

    return stamps, ci

def moviemany():
    for t in tics:
        check_crm(t, movie=True, maxtimespan=600)
