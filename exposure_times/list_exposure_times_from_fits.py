#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a bunch of FITS template spectra, and list their intrinsic magnitudes (as saved in the FITS file), and the
exposure times needed to observe them if they were at some particular reference magnitude.
"""

import os
from os import path as os_path
import glob
import numpy as np
from astropy.io import fits
import argparse
import logging

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_fourfs import FourFS

our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input',
                    required=True,
                    dest="input",
                    help="A filename wildcard where we can find the template spectra to operate on.")
parser.add_argument('--library',
                    dest="library",
                    default="louise_templates",
                    help="The spectrum library to import the templates into.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where 4FS package is installed.")
parser.add_argument('--photometric-band',
                    required=False,
                    default="SDSS_r",
                    dest="photometric_band",
                    help="The name of the photometric band in which the magnitude is specified.")
parser.add_argument('--magnitude',
                    required=False,
                    default="15",
                    dest="magnitude",
                    help="The magnitude to assume when calculating exposure times for each object.")
args = parser.parse_args()

# Start logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Calculating magnitudes and exposure times for templates")

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Turn set of templates into a SpectrumLibrary with path specified above
library_path = os_path.join(workspace, args.library)
library = SpectrumLibrarySqlite(path=library_path, create=True)

templates = glob.glob(args.input)
templates.sort()

# For calculating exposure times, assume a specified magnitude
magnitude = float(args.magnitude)

# Instantiate 4FS wrapper
# NB: Here we are requiring SNR/pixel=100 in GalDiskHR_545NM
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
    magnitude=magnitude,
    magnitude_unreddened=False,
    photometric_band=args.photometric_band,
    hrs_use_snr_definitions=["GalDiskHR_545NM", "GalDiskHR_545NM", "GalDiskHR_545NM"],
    run_hrs=True, run_lrs=False,
    snr_list=(100,),
    snr_per_pixel=False
)

for template_index, template in enumerate(templates):
    name = "template_{:08d}".format(template_index)

    # Open fits spectrum
    f = fits.open(template)
    data = f[1].data
    wavelengths = data['LAMBDA']
    fluxes = data['FLUX']

    # Open ASCII spectrum
    # f = np.loadtxt(template).T
    # wavelengths = f[0]
    # fluxes = f[1]

    # Create 4GP spectrum object
    spectrum = Spectrum(wavelengths=wavelengths,
                        values=fluxes,
                        value_errors=np.zeros_like(wavelengths),
                        metadata={
                            "Starname": name,
                            "imported_from": template
                        })

    # Work out magnitude
    mag_intrinsic = spectrum.photometry(args.photometric_band)

    # Pass template to 4FS
    degraded_spectra = etc_wrapper.process_spectra(
        spectra_list=((spectrum, None),)
    )

    index = degraded_spectra["HRS"].keys()[0]
    exposure_time = degraded_spectra["HRS"][index][100]["spectrum"].metadata["exposure"]  # seconds

    # Print output
    print "{:100s} {:6.3f} {:6.3f}".format(template, mag_intrinsic, exposure_time)

    # Insert spectrum object into spectrum library
    library.insert(spectra=spectrum, filenames=os_path.split(template)[1])
