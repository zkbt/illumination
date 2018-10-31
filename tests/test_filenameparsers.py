from illumination.sequences.filenameparsers import *

def test_parsers():

    for f in [  'some-little-filename.fits',
                'cam1-ccd2-00001.fits',
                'tess2018220104526-00004907-1-crm-ffi-ccd1.fits',
                'tess2018220104526-00005279-4-crm-ffi_dehoc.fits']:

        # test the filename parsers
        print(f, flexible_filenameparser(f))

if __name__ == '__main__':
    test_parsers()
