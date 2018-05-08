#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a bunch of template spectra in a SpectrumLibrary, and list the exposure times needed to observe them if they
were at some particular reference magnitude.
"""

import os
from os import path as os_path
import numpy as np
import argparse
import logging

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_fourfs import FourFS

our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library',
                    required=True,
                    dest="library",
                    help="The spectrum library where we can find the template spectra to operate on.")
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

# For calculating exposure times, assume a specified magnitude
magnitude = float(args.magnitude)

# Instantiate 4FS wrapper
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

# Open input SpectrumLibrary
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                workspace=workspace,
                                                extra_constraints={"continuum_normalised": 0}
                                                )
input_library, input_spectra_ids, input_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

# Loop over spectra to process
for input_spectrum_id in input_spectra_ids:
    logger.info("Working on <{}>".format(input_spectrum_id['filename']))

    # Open Spectrum data from disk
    input_spectrum_array = input_library.open(ids=input_spectrum_id['specId'])
    input_spectrum = input_spectrum_array.extract_item(0)

    # Look up the name of the star we've just loaded
    spectrum_matching_field = 'uid' if 'uid' in input_spectrum.metadata else 'Starname'
    object_name = input_spectrum.metadata[spectrum_matching_field]

    # Search for the continuum-normalised version of this same object
    search_criteria = input_spectra_constraints.copy()
    search_criteria[spectrum_matching_field] = object_name
    search_criteria['continuum_normalised'] = 1
    continuum_normalised_spectrum_id = input_library.search(**search_criteria)

    # Check that continuum-normalised spectrum exists
    assert len(continuum_normalised_spectrum_id) == 1, "Could not find continuum-normalised spectrum."

    # Load the continuum-normalised version
    input_spectrum_continuum_normalised_arr = input_library.open(
        ids=continuum_normalised_spectrum_id[0]['specId'])
    input_spectrum_continuum_normalised = input_spectrum_continuum_normalised_arr.extract_item(0)

    # Work out magnitude
    mag_intrinsic = input_spectrum.photometry(args.photometric_band)

    # Pass template to 4FS
    degraded_spectra = etc_wrapper.process_spectra(
        spectra_list=((input_spectrum, input_spectrum_continuum_normalised),)
    )

    index = degraded_spectra["HRS"].keys()[0]
    exposure_time = degraded_spectra["HRS"][index][100]["spectrum"].metadata["exposure"]  # seconds

    # Print output
    print "{:100s} {:6.3f} {:6.3f}".format(object_name, mag_intrinsic, exposure_time)
