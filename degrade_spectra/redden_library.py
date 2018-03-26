#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a library of spectra, perhaps generated by Turbospectrum, and redden them.
"""

import argparse
import os
from os import path as os_path
import hashlib
import time
import re
import logging

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_degrade import SpectrumReddener

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-library',
                    required=False,
                    default="demo_stars",
                    dest="input_library",
                    help="The name of the SpectrumLibrary we are to read input spectra from. Stars may be filtered by "
                         "parameters by placing a comma-separated list of constraints in [] brackets after the name of "
                         "the library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                         "range.")
parser.add_argument('--output-library',
                    required=False,
                    default="demo_stars_reddened",
                    dest="output_library",
                    help="The name of the SpectrumLibrary we are to feed reddened spectra into.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--ebv-list',
                    required=False,
                    default="0.05,0.1,0.5,0.9,1.3,1.5,2,2.3",
                    dest="ebv_list",
                    help="Specify a comma-separated list of the E_BV values we are to use when reddening spectra.")
parser.add_argument('--create',
                    required=False,
                    action='store_true',
                    dest="create",
                    help="Create a clean SpectrumLibrary to feed synthesized spectra into")
parser.add_argument('--no-create',
                    required=False,
                    action='store_false',
                    dest="create",
                    help="Do not create a clean SpectrumLibrary to feed synthesized spectra into")
parser.set_defaults(create=True)
parser.add_argument('--log-file',
                    required=False,
                    default="/tmp/reddening_{}.log".format(pid),
                    dest="log_to",
                    help="Specify a log file where we log our progress.")
args = parser.parse_args()

logger.info("Reddening spectra with arguments <{}> <{}>".format(args.input_library,
                                                                args.output_library))

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Open input SpectrumLibrary
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=args.input_library,
                                                workspace=workspace,
                                                extra_constraints={"continuum_normalised": 0}
                                                )
input_library, input_spectra_ids, input_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

# Create new SpectrumLibrary
library_name = re.sub("/", "_", args.output_library)
library_path = os_path.join(workspace, library_name)
output_library = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Photometric bands to save extinction values for
photometric_bands = ["SDSS_r", "SDSS_g", "GROUND_JOHNSON_V", "GROUND_JOHNSON_B"]

# Reddening values
ebv_list = [float(item.strip()) for item in args.ebv_list.split(",")]

# Loop over spectra to process
with open(args.log_to, "w") as result_log:
    for input_spectrum_id in input_spectra_ids:
        logger.info("Working on <{}>".format(input_spectrum_id['filename']))
        # Open Spectrum data from disk
        input_spectrum_array = input_library.open(ids=input_spectrum_id['specId'])
        input_spectrum = input_spectrum_array.extract_item(0)

        # Look up the name of the star we've just loaded
        spectrum_matching_field = 'uid' if 'uid' in input_spectrum.metadata else 'Starname'
        object_name = input_spectrum.metadata[spectrum_matching_field]

        # Write log message
        result_log.write("\n[{}] {}... ".format(time.asctime(), object_name))
        result_log.flush()

        # Search for the continuum-normalised version of this same object
        search_criteria = input_spectra_constraints.copy()
        search_criteria[spectrum_matching_field] = object_name
        search_criteria['continuum_normalised'] = 1
        continuum_normalised_spectrum_id = input_library.search(**search_criteria)

        # Check that continuum-normalised spectrum exists
        assert len(continuum_normalised_spectrum_id) == 1, "Could not find continuum-normalised spectrum."

        # Load the continuum-normalised version
        input_spectrum_continuum_normalised_arr = input_library.open(ids=continuum_normalised_spectrum_id[0]['specId'])
        input_spectrum_continuum_normalised = input_spectrum_continuum_normalised_arr.extract_item(0)

        # Process spectra through reddening model
        reddener = SpectrumReddener(input_spectrum=input_spectrum)

        # Loop over different values of E(B-V)
        for e_bv in ebv_list:
            unique_id = hashlib.md5(os.urandom(32).encode("hex")).hexdigest()[:16]
            reddened_spectrum = reddener.redden(e_bv=e_bv)

            metadata = {"e_bv": e_bv, "uid": unique_id}

            # Work out extinction values in photometric bands of interest
            for band in photometric_bands:
                metadata["A_{}".format(band)] = (reddened_spectrum.photometry(band=band) -
                                                 input_spectrum.photometry(band=band))

            # Save spectra
            output_library.insert(spectra=reddened_spectrum,
                                  filenames=input_spectrum_id['filename'],
                                  metadata_list=metadata)
            output_library.insert(spectra=input_spectrum_continuum_normalised,
                                  filenames=continuum_normalised_spectrum_id[0]['filename'],
                                  metadata_list=metadata)
