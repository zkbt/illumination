#tic = 248093171
from playground.cosmics.stamps import *
from playground.tv.illustrations import CubesIllustration
from playground.tv.animation import animate

possible = glob.glob('/pdo/ramp/zkbt/orbit-8193/stamps/spm*/tic*_*_cam*_spm*_*s.npy')
tics = [int(f.split('tic')[1].split('_')[0]) for f in possible]

#for tic in tics:

def checkcrm(tic=tics[0], movie=False, mintime = 1209031557, maxtimespan=600):

    stamps = {}
    kinds = ['2s', 'nocrm', 'crm']
    for spm, name in zip([1,2,3], kinds):
        search = '/pdo/ramp/zkbt/orbit-8193/stamps/spm*/tic{}_*_cam*_spm{}_*s.npy'.format(tic, spm)
        file = glob.glob(search)[0]
        stamps[name] = Stamp(file)

    stamps['difference'] = copy.copy(stamps['nocrm'])
    stamps['difference'].photons = stamps['nocrm'].photons - stamps['crm'].photons*5/4
    stamps['difference'].consider()

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
    ci = CubesIllustration([stamps[k] for k in todisplay], names=todisplay)
    ci.plot()

    if movie:
        animate(ci, mintime=mintime, maxtimespan=maxtimespan, filename=os.path.join(basedirectory, '{}-crm.gif'.format(tic)))

    return stamps, ci

def moviemany():
    for t in tics:
        checkcrm(t, movie=True, maxtimespan=600)
