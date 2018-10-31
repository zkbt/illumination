'''
`illumination` is a set of tools for display TESS pixels in Python and
matplotlib. It can be used for automated visualizations and animations,
so you can pull out your loupe and flyswatter and start looking at stars.
'''

# make sure we keep track of the version
from .version import __version__

# import some of the basics to be generally available
from .illustrations import *
from .zoom import *
from .sequences import *
from .wrappers import *
from .cartoons import *
