from illumination.imports import *
from illumination.cartoons import *
from illumination.wrappers import *

filetemplate = "cam{}-ccd{}-{}.fits"
directory = "examples/"
mkdir(directory)

imagedirectory = os.path.join(directory, "images")
mkdir(imagedirectory)


def create_some_files():
    """
    Create a little ensemble of files.

    This is a helper for the tests below.
    """
    for cam in [1, 2, 3, 4]:
        for ccd in [1, 2, 3, 4]:
            for n in range(3):
                filename = os.path.join(
                    imagedirectory, filetemplate.format(cam, ccd, n)
                )
                try:
                    create_test_fits(400, 400).writeto(filename)
                except (OSError, IOError):
                    print("{} already exists".format(filename))


def test_organize():
    """
    Test the tool for organizing filenames into
    a reasonably organized collection of sequences.
    """

    # create a bunch of files
    create_some_files()
    pattern = os.path.join(imagedirectory, "cam*-ccd*-0000.fits")


def test_illustratefits():
    """
    Test the basic functionality of `illustratefits`.
    Can it handle one/many cameras, and one/many CCDs?
    """

    # create a bunch of files
    create_some_files()
    x = {"many": "*", "one": 1}
    for camera in ["one", "many"]:
        for ccd in ["one", "many"]:

            # create, plot, save, and animate the illustration
            pattern = os.path.join(
                imagedirectory, filetemplate.format(x[camera], x[ccd], "*")
            )
            i = illustratefits(pattern)
            i.plot()
            filename = os.path.join(
                directory, "illustratefits-camera={}-ccd={}.png".format(camera, ccd)
            )
            i.savefig(filename)
            i.animate(filename=filename.replace("png", "mp4"))


def test_illustratefitswithzoom(zoomposition=(30, 70), zoomsize=(10, 10)):

    print("\nTesting a Single Camera with a Zoom.")
    create_some_files()

    # create the illustration
    illustration = illustratefits(
        os.path.join(imagedirectory, filetemplate.format(1, 1, "*")),
        zoomposition=zoomposition,
        zoomsize=zoomsize,
    )
    # plot and animate
    illustration.plot()
    filename = os.path.join(directory, "illustatefits-zoom-animation.mp4")
    illustration.animate(filename)
    print("Take a look at {} and see what you think!".format(filename))


if __name__ == "__main__":
    test_illustratefits()
    test_illustratefitswithzoom()
