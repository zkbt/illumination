from __future__ import print_function
import os, copy, subprocess, glob, shutil, warnings
import numpy as np, matplotlib.pyplot as plt

import matplotlib.animation as ani
import matplotlib.gridspec as gs

from astropy.io import fits, ascii
from astropy.time import Time
from astropy.stats import mad_std
import astropy.units as u

from .talker import Talker

def mkdir(path):
		'''
		A mkdir that doesn't complain if it already exists.
		'''
		try:
			os.mkdir(path)
			print("made {}".format(path))
		except:
			pass

def mad(x):
		'''
		Returns the median absolute deviation from the median,
				a robust estimator of a distribution's width.

				For a Gaussian distribution, sigma~1.48*MAD.
		'''
		med = np.median(x)
		return np.median(np.abs(x - med))

def shared_directory(files, verbose=False):
	'''
	Find the shared base directory amongst a list of files.

	Parameters
	----------

	files : list
		A list of filenames.

	Returns
	-------

	shared : str
		A filepath that is the shared across all the files.
	'''

	for i in range(len(files[0])):
		shared = files[0][:i+1]
		if verbose:
			print('"{}"'.format(shared))
		for f in files:
			if f[:i+1] != shared:
				if verbose:
					print('Huzzah! "{}" is shared across {} files.'.format(shared[:-1], len(files)))
				return shared[:-1]


def binto(x=None, y=None, yuncertainty=None,
			binwidth=0.01,
			test=False,
			robust=True,
			sem=True,
			verbose=False):
	'''Bin a timeseries to a given binwidth,
		returning both the mean and standard deviation
			(or median and approximate robust scatter).'''

	if test:
		n = 1000
		x, y = np.arange(n), np.random.randn(n) - np.arange(n)*0.01 + 5
		bx, by, be = binto(x, y, binwidth=20)
		plt.figure('test of craftroom.binto')
		plt.cla()
		plt.plot(x, y, linewidth=0, markersize=4, alpha=0.3, marker='.', color='gray')
		plt.errorbar(bx, by, be, linewidth=0, elinewidth=2, capthick=2, markersize=10, alpha=0.5, marker='.', color='blue')
		return

	min, max = np.min(x), np.max(x)
	bins = np.arange(min, max+binwidth, binwidth)
	count, edges = np.histogram(x, bins=bins)
	sum, edges = np.histogram(x, bins=bins, weights=y)

	if yuncertainty is not None:
		count, edges = np.histogram(x, bins=bins)
		numerator, edges = np.histogram(x, bins=bins, weights=y/yuncertainty**2)
		denominator, edges = np.histogram(x, bins=bins, weights=1.0/yuncertainty**2)
		mean = numerator/denominator
		std = np.sqrt(1.0/denominator)
		error = std
		if False:
			for i in range(len(bins)-1):
				print(bins[i], mean[i], error[i], count[i])
			a = raw_input('???')
	else:
		if robust:
			n= len(sum)
			mean, std = np.zeros(n) + np.nan, np.zeros(n) + np.nan
			for i in range(n):
				inbin = (x>edges[i])*(x<=edges[i+1])
				mean[i] = np.median(y[inbin])
				std[i] = 1.48*mad(y[inbin])
		else:
			if yuncertainty is None:
				mean = sum.astype(np.float)/count
				sumofsquares, edges = np.histogram(x, bins=bins, weights=y**2)
				std = np.sqrt(sumofsquares.astype(np.float)/count - mean**2)*np.sqrt(count.astype(np.float)/np.maximum(count-1.0, 1.0))
		if sem:
			error = std/np.sqrt(count)
		else:
			error = std


	x = 0.5*(edges[1:] + edges[:-1])
	return x, mean, error

	if yuncertainty is not None:
		print("Uh-oh, the yuncertainty feature hasn't be finished yet.")

	if robust:
		print("Hmmm...the robust binning feature isn't finished yet.")
