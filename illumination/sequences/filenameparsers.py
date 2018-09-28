'''
Define some filename parsers than can pull details from filenames,
and convert them to dictionaries.
'''

from ..imports import *

def qlp_filenameparser(filename):
    '''
    Parse a QLP-type file like
    "tess2018220104526-00004907-1-crm-ffi-ccd1.fits"
    into a dictionary of important information.
    '''

    d = {}
    d['filename'] = os.path.basename(filename)
    s = d['filename'].split('.fit')[0]
    components = s.split('-')
    d['cadence'] = float(components[1])
    d['camera'] = int(components[2])
    d['crm'] = components[3]
    d['type'] = components[4]
    d['ccd'] = s[s.index('ccd'):][3]
    return d

def qlp_fullcamera_filenameparser(filename):
    '''
    Parse a QLP-type file like
    "tess2018220104526-00005279-4-crm-ffi_dehoc.fits"
    into a dictionary of important information.
    '''

    d = {}
    d['filename'] = os.path.basename(filename)
    s = d['filename'].split('.fit')[0]
    components = s.split('-')
    d['cadence'] = float(components[1])
    d['camera'] = int(components[2])
    d['crm'] = components[3]
    d['type'] = components[4]
    return d

def flexible_filenameparser(filename):
    try:
        return qlp_filenameparser(filename)
    except:
        return qlp_fullcamera_filenameparser(filename)
