# illumination

Sometimes it can be really helpful to take your image of the sky, set it up on your light box, and illuminate it so you can investigate it closely with your loupe and fly-swatter. This package provides tools to make pretty illustrations and animations from time-series imaging data. Documentation and examples can be found at [zkbt.github.io/illumination/](https://zkbt.github.io/illumination/)

### Installation

If you want to use this package without editing it directly, the easiest way to install it is via
```
pip install illumination
```

If you want to be able to modify the code yourself, please also feel free to fork/clone this repository onto your own computer and install directly from that editable package. For example, this might look like:
```
git clone https://github.com/zkbt/illumination.git
cd illumination/
pip install -e .
# or, if you don't have root access ...
pip install -e . --user
```
This will download the current `illumination` repository to your current directory, and then link the installed version of the `illumination` package to this local repository. Changes you make to the code in the repository should be reflected in what Python sees when it tries to `import illumination`.

To be able to create movies, you will likely want to install `ffmpeg`. To do so, run the command:
```
conda install -c conda-forge ffmpeg
```

### Compatability 
This code sat in a quiet corner for a while, eventually falling asleep and letting the world pass it by. In that intervening time, some initial attempts to interface with `lightkurve` tools and data formats for TESS and Kepler became obsolete. We're poking at it in June 2023, but we want to warn you that in jumping from version 0.0.12 to 0.1.0, the code loses the ability to directly interface with TESS/Kepler light curves or target pixel files. 