#!/usr/bin/env python

# The template for this setup.py came from Tim Morton,
# who I understand took it from Dan F-M. And then Geert
# Barentsen and Christina Hedges helped explain a few
# more neat tips. Thanks all!


import os
import sys
from setuptools import setup, find_packages


# a little kludge to be able to get the version number from the package
from illumination.version import __version__

setup(name = "illumination",
    version = __version__,
    description = "Python tools for visualizing astronomical images, particularly from the NASA TESS mission.",
    long_description = "", # need to add
    author = "Zach Berta-Thompson",
    author_email = "zach.bertathompson@colorado.edu",
    url = "https://tessgit.mit.edu/zkbt/playground",
    packages = find_packages(),
    package_data = {'illumination':[]},
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
