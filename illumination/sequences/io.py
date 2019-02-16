from ..imports import *
import skimage.io
from astropy.io import fits

def read_fits(path, ext_image=1):
    '''
    Read an image from a FITS file.
    '''

    # open the fits file
    hdu_list = fits.open(path)

    # make sure we're asking for a reasonable image extension
    ext_image = np.minimum(ext_image, len(hdu_list)-1)

    # extract the image data from the FITs file
    image = hdu_list[ext_image].data

    print('read a {} grayscale image from {}'.format(image.shape, path))

    # return the image
    return image

def read_rgb(path):
    '''
    Read an image (.jpg, .png, .tif, .gif)
    into three numpy arrays, one each for
    the brightness in Red, Green, Blue.

    Parameters
    ----------
    path : str
        The filename of the image to read.

    Returns
    -------
    r, g, b : arrays
        The brightness of the image in each of the
        red, green, blue wavelength ranges.
    '''

    # read a (rows x cols x 3) image
    rgb = skimage.io.imread(path, as_gray=False)

    if len(rgb.shape) == 2:
        # if grayscale already, set the red, green, blue channels to be equal
        r = rgb
        g = rgb
        b = rgb

    else:
        # pull out the red, green, blue channels
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]

    # print an update
    print('read a {} RGB image from {}'.format(rgb.shape, path))

    # return the three separate images
    return r, g, b

def read_gray(path):
    '''
    Read an image (.jpg, .png, .tif, .gif)
    into one numpy array, where the individual
    RGB channels have been merged together
    into one single grayscale image.

    Parameters
    ----------
    path : str
        The filename of the image to read.

    Returns
    -------
    gray : array
        The brightness of the image, estimated
        from a weighted average across the red,
        green, and blue bandpasses.
    '''

    # load the image as gray-scale
    image = skimage.io.imread(path, as_gray=True)

    # print an update
    print('read a {} grayscale image from {}'.format(image.shape, path))

    # return the image
    return image

def read_image(path, **kw):
    '''
    Read an image, being flexible about what kind of image it is.

    Parameters
    ----------
    path : str
        The filename of the image to read.

    Returns
    -------
    gray : array
        The brightness of the image, as a 2D numpy array.
    '''

    if '.fit' in path:
        return read_fits(path, **kw)
    else:
        return read_gray(path, **kw)

def write_image(image, filename='image.jpg'):
    '''
    Write a numpy array to an image file.

    Parameters
    ----------
    image : array
        The image to save.
    filename : str
        The filename where the image should be saved.
    '''

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        # save the image
        if '.fit' in filename:
            hdu = fits.PrimaryHDU(data=image).writeto(filename, overwrite=True)
        else:
            skimage.io.imsave(filename, image)

    # print an update
    print('saved {} image to {}'.format(image.shape, filename))

def compile_rgb(red, green, blue):
    incolor = np.zeros_like(red)[:,:,np.newaxis]*np.ones(3).astype(np.int)
    incolor[:,:,0] = red
    incolor[:,:,1] = green
    incolor[:,:,2] = blue
    return incolor

# read different image file types (png, tiff, giff)
# write a guesser to read an arbitrary image (based on filename)
# read a movies as a sequence of images (?)
# (add URL capability for the path)?
