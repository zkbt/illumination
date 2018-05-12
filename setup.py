#!/usr/bin/env python

# The template for this setup.py came from Tim Morton,
# who I understand took it from Dan F-M. And then Geert
# Barentsen and Christina Hedges helped explain a few
# more neat tips. Thanks all!


import os
import sys
from setuptools import setup, find_packages


# a little kludge to be able to get the version number from the package
import sys
if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins
builtins.__PLAYGROUNDSETUP__ = True
import playground
version = playground.__version__

setup(name = "playground",
    version = version,
    description = "Space to play with early TESS pixels.",
    long_description = "For usage, installation, and discussion, please visit https://tessgit.mit.edu/zkbt/playground",
    author = "Zach Berta-Thompson",
    author_email = "zach.bertathompson@colorado.edu",
    url = "https://tessgit.mit.edu/zkbt/playground",
    packages = find_packages(),
    package_data = {'playground':[]},
    include_package_data=False,
    scripts = [],
    classifiers=[
      'Intended Audience :: Science/Research',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Astronomy'
      ],
    install_requires=['numpy', 'matplotlib', 'scipy', 'astropy'],
    zip_safe=False,
    license='MIT',
)
