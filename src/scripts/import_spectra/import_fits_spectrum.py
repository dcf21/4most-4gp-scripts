#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python import_fits_spectrum.py>, but <./import_fits_spectrum.py> will not work.

"""
Take a FITS file containing a spectrum, and import it into a spectrum library.
"""

import argparse
import logging
import os
import re
from os import path as os_path

import numpy as np
from astropy.io import fits
from fourgp_speclib import SpectrumLibrarySqlite, Spectrum

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Spectrum library to insert spectrum into.")
parser.add_argument('--filename', required=True, dest='filename',
                    help="The filename of the FITS file to import.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--create',
                    action='store_true',
                    dest="create",
                    help="Create a clean spectrum library to feed output spectra into. Will throw an error if "
                         "a spectrum library already exists with the same name.")
parser.add_argument('--no-create',
                    action='store_false',
                    dest="create",
                    help="Do not create a clean spectrum library to feed output spectra into.")
parser.set_defaults(create=True)
args = parser.parse_args()

# Set path to workspace where we create libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")
os.system("mkdir -p {}".format(workspace))

# Create new spectrum library
library_name = re.sub("/", "_", args.library)
library_path = os_path.join(workspace, library_name)
library = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Open fits spectrum
f = fits.open(args.filename)
data = f[1].data

wavelengths = data['LAMBDA']
fluxes = data['FLUX']

# Create 4GP spectrum object
spectrum = Spectrum(wavelengths=wavelengths,
                    values=fluxes,
                    value_errors=np.zeros_like(wavelengths),
                    metadata={
                        "imported_from": args.filename
                    })

# Insert spectrum object into spectrum library
library.insert(spectra=spectrum, filenames=os_path.split(args.filename)[1])
