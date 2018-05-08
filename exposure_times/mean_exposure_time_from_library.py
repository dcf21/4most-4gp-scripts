#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a bunch of template spectra in a SpectrumLibrary, and list the exposure times needed to observe them if they
were at some particular reference magnitude.
"""

from os import path as os_path
import numpy as np
import argparse
import logging

from fourgp_speclib import SpectrumLibrarySqlite
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
parser.add_argument('--snr-list',
                    required=False,
                    default="10,12,14,16,18,20,23,26,30,35,40,45,50,80,100,130,180,250",
                    dest="snr_list",
                    help="Specify a comma-separated list of the SNRs that 4FS is to degrade spectra to.")
parser.add_argument('--snr-definitions-lrs',
                    required=False,
                    default="",
                    dest="snr_definitions_lrs",
                    help="Specify the SNR definitions to use for the R, G and B bands of 4MOST LRS.")
parser.add_argument('--snr-definitions-hrs',
                    required=False,
                    default="GalDiskHR_545NM",
                    dest="snr_definitions_hrs",
                    help="Specify the SNR definitions to use for the R, G and B bands of 4MOST HRS.")
parser.add_argument('--run-hrs',
                    action='store_true',
                    dest="run_hrs",
                    help="Set 4FS to produce output for 4MOST HRS")
parser.add_argument('--no-run-hrs',
                    action='store_false',
                    dest="run_hrs",
                    help="Set 4FS not to produce output for 4MOST HRS")
parser.set_defaults(run_hrs=True)
parser.add_argument('--run-lrs',
                    action='store_true',
                    dest="run_lrs",
                    help="Set 4FS to produce output for 4MOST LRS")
parser.add_argument('--no-run-lrs',
                    action='store_false',
                    dest="run_lrs",
                    help="Set 4FS not to produce output for 4MOST LRS")
parser.set_defaults(run_lrs=False)
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

# Definitions of SNR
if len(args.snr_definitions_lrs) < 1:
    snr_definitions_lrs = None
else:
    snr_definitions_lrs = args.snr_definitions_lrs.split(",")
    if len(snr_definitions_lrs) == 1:
        snr_definitions_lrs *= 3
    assert len(snr_definitions_lrs) == 3

if len(args.snr_definitions_hrs) < 1:
    snr_definitions_hrs = None
else:
    snr_definitions_hrs = args.snr_definitions_hrs.split(",")
    if len(snr_definitions_hrs) == 1:
        snr_definitions_hrs *= 3
    assert len(snr_definitions_hrs) == 3

# List of SNRs we are to degrade spectra to
snr_list = [float(item.strip()) for item in args.snr_list.split(",")]

# Instantiate 4FS wrapper
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
    magnitude=magnitude,
    magnitude_unreddened=False,
    photometric_band=args.photometric_band,
    run_lrs=args.run_lrs,
    run_hrs=args.run_hrs,
    lrs_use_snr_definitions=snr_definitions_lrs,
    hrs_use_snr_definitions=snr_definitions_hrs,
    snr_list=snr_list,
    snr_per_pixel=False
)

# Open input SpectrumLibrary
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                workspace=workspace,
                                                extra_constraints={"continuum_normalised": 0}
                                                )
input_library, input_spectra_ids, input_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

# Initialise output data structure
output = {}  # output["HRS"][snr] = list of exposure times in seconds

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

    # Pass template to 4FS
    degraded_spectra = etc_wrapper.process_spectra(
        spectra_list=((input_spectrum, input_spectrum_continuum_normalised),)
    )

    # Process degraded spectra
    for mode in degraded_spectra:
        for index in degraded_spectra[mode]:
            for snr in degraded_spectra[mode][index]:
                exposure_time = degraded_spectra[mode][index][snr]["spectrum"].metadata["exposure"]  # seconds

                if mode not in output:
                    output[mode] = {}
                if snr not in output[mode]:
                    output[mode][snr] = []
                output[mode][snr].append(exposure_time)

# Print output
for mode in output:
    snr_values = output[mode].keys()
    snr_values.sort()
    for snr in snr_values:
        exposure_time_mean = np.mean(output[mode][snr])
        exposure_time_sd = np.std(output[mode][snr])
        print "{:6s} {:6.1f} {:6.3f} {:6.3f}".format(mode, snr, exposure_time_mean, exposure_time_sd)
