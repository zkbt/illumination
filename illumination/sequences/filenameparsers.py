'''
Define some filename parsers than can pull details from filenames,
and convert them to dictionaries.
'''

from ..imports import *

def generic_filenameparser(filename):
    '''
    Parse a general file like, for example,
    "some-little-filename.fits"
    into a dictionary of important information.

    (This one is meant to be expanded upon elsewhere.)

    Parameters
    ----------
    filename : str
        The filename of a single image.

    Returns
    -------
    features : dict
        This dictionary of details contains the filename, (and you
        should add some other keywords too, if you want to expand
        upon this.)
    '''
    d = {}
    d['filename'] = os.path.basename(filename)
    return d

def explicit_filenameparser(filename):
    '''
    Parse a file that explicitly specifies ccd and camera
    like, for example, "cam1-ccd2-00001.fits"
    into a dictionary of important information.

    (This one is meant to be expanded upon elsewhere.)

    Parameters
    ----------
    filename : str
        The filename of a single image.

    Returns
    -------
    features : dict
        This dictionary of details contains the filename, camera, and CCD.
    '''
    d = {}
    d['filename'] = os.path.basename(filename)
    s = d['filename'].split('.fit')[0]
    d['camera'] = s[s.index('cam'):][3]
    d['ccd'] = s[s.index('ccd'):][3]
    return d

def tessqlp_filenameparser(filename):
    '''
    Parse a QLP-type (single-CCD) file like, for example,
    "tess2018220104526-00004907-1-crm-ffi-ccd1.fits"
    into a dictionary of important information.

    Parameters
    ----------
    filename : str
        The filename of a single FITS image.

    Returns
    -------
    features : dict
        This dictionary of details contains the filename, the cadence number,
        the camera number, whether or not crm was applied, the image type, and
        the CCD number.
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

def tessqlp_fullcamera_filenameparser(filename):
    '''
    Parse a QLP-type file like, for example,
    "tess2018220104526-00005279-4-crm-ffi_dehoc.fits"
    into a dictionary of important information.

    Parameters
    ----------
    filename : str
        The filename of a single FITS image.

    Returns
    -------
    features : dict
        This dictionary of details contains the filename, the cadence number,
        the camera number, whether or not crm was applied, and the image type.
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
    '''
    Parse a generic FITS filename,
    trying to guess an appropriate method for it,
    and create a dictionary of important information.

    Parameters
    ----------
    filename : str
        The filename of a single FITS image.

    Returns
    -------
    features : dict
        This dictionary of details contains at least the filename, and
        hopefully some other stuff too.
    '''

    # filename parsers, in order of priority
    parsers = [ tessqlp_filenameparser,
                tessqlp_fullcamera_filenameparser,
                explicit_filenameparser,
                generic_filenameparser]

    # try each parser in turn, moving to the next if one complains
    for p in parsers:
        try:
            return p(filename)
        except:
            pass
