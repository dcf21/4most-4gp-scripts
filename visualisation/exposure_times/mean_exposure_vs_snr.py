#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a SpectrumLibrary and tabulate the average exposure time at each SNR within it.
"""

import argparse
from os import path as os_path
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, action="append", dest='libraries',
                    help="Library of spectra we should output stellar labels for.")
parser.add_argument('--output-file', default="/tmp/exposure_times_vs_snr.dat", dest='output_file',
                    help="Data file to write output to.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "..", "workspace")

# Construct list of exposure times at each SNR
exposures_by_snr = {}

# Open output data file
with open(args.output_file, "w") as output:
    # Open spectrum libraries in turn
    for library in args.libraries:
        library_path = os_path.join(workspace, library)
        library_object = SpectrumLibrarySqlite(path=library_path, create=False)

        # Loop over objects in each spectrum library
        constraints = {"continuum_normalised": 1}

        # Loop over objects in SpectrumLibrary
        for item in library_object.search(**constraints):
            metadata = library_object.get_metadata(ids=item['specId'])[0]

            exposure = metadata['exposure']
            snr = metadata['SNR']

            if snr not in exposures_by_snr:
                exposures_by_snr[snr] = []

            exposures_by_snr[snr].append(exposure)

# Make list of unique SNR values
unique_snrs = set(exposures_by_snr.keys())
unique_snrs_sorted = list(unique_snrs)
unique_snrs_sorted.sort()

# Write output data file
with open(args.output_file,"w") as f:
    f.write("# SNR/pixel Exposure time\n")
    for snr in unique_snrs_sorted:
        f.write("{0:.3f}  {1:.3f}\n".format(snr, np.mean(exposures_by_snr[snr])))

