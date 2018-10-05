from .Sequence import *
from .FITS_Sequence import *
from .Stamp_Sequence import *
from .TPF_Sequence import *
from .Timeseries_Sequence import *

def make_image_sequence(initial, *args, **kwargs):
    '''
    Initialize a Sequence for viewing with tv.

    This is a general wrapper that *tries* to
    guess what kind of Sequence to make,
    based solely on the inputs. If this fails,
    you may need to specify the Sequence explicitly.

    Parameters
    -----------

        initial : (many possible types)
                This is the input that initializes an image sequence.
                    - single FITS filename, and an extension to use.
                    - list of FITS filenames, and an extension to use.
                    - a glob pattern to search for FITS files (and extension)
                    - single FITS HDUList, and an extension to use.
                    - list of loaded FITS HDULists, and an extension to use.
                    - a Stamp object from the `cosmics` package.

        *args
            Positional arguments will be passed on to whatever Sequence is initialized

        **kwargs
            Keyword arguments will be passed on to whatever Sequence is initialized

    '''

    # is it already a sequence?
    if issubclass(initial.__class__, Sequence):
        return initial
    # is it empty? return an empty sequence
    elif initial is [] or initial is None:
        return Sequence()
    # is it a Stamp?
    elif type(initial) == Stamp:
        return Stamp_Sequence(initial, *args, **kwargs)
    elif type(initial) == np.ndarray:
        return Image_Sequence(initial, **kwargs)
    else:
        # try:
        #	# is initial a 1D thing?
        #	assert(len(np.shape(initial))==1 or isinstance(initial, LightCurve))
        #	return Timeseries_Sequence(initial, *args, **kwargs)
        # except AssertionError:

        # is it a TPF (or can it be used to make one, like a filename)?
        try:
            assert(isinstance(initial, TargetPixelFile))
            return TPF_Sequence(initial, *args, **kwargs)
        # if nothing else, assume it is a FITS_Sequence
        except (AttributeError, AssertionError):
            return FITS_Sequence(initial, *args, **kwargs)
