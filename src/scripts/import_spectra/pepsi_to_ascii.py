#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python import_pepsi.py>, but <./import_pepsi.py> will not work.

"""
Take the FITS files containing the PEPSI sample, and turn them into ASCII data files.
"""

import argparse
import os
from os import path as os_path
import numpy as np
import glob
import logging
import re
from astropy.io import fits

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../../../..")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--fits-path', default="../../../../pepsi/", dest='fits_path',
                    help="The path to the FITS file to import.")
args = parser.parse_args()

# Make directory to hold ASCII spectra
output_directory = "/tmp/pepsi_ascii"
os.system("mkdir -p {}".format(output_directory))

# Open fits spectrum
for item in glob.glob(os_path.join(args.fits_path, "*.all6")):
    filename = os_path.split(item)[1]

    # Open FITS file
    f = fits.open(item)

    # Extract continuum-normalised spectrum from FITS file
    data = f[1].data

    wavelengths = data['Arg']
    flux = data['Fun']
    flux_errors = data['Var']

    filename_out = "{}/{}.dat".format(output_directory, filename)
    np.savetxt(filename_out, np.transpose( [wavelengths, flux, flux_errors] ))

