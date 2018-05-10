__version__ = '0.0.0'

# specify whether we're calling this from within setup.py
try:
    __PLAYGROUNDSETUP__
except NameError:
    __PLAYGROUNDSETUP__ = False

if not __PLAYGROUNDSETUP__:
    # (run this stuff if it's not form within setup.py)
    pass
