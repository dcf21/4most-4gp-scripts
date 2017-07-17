#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take a SpectrumLibrary and tabulate the stellar parameters within it.
"""

import argparse
from os import path as os_path

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, action="append", dest='libraries',
                    help="Library of spectra we should output stellar labels for.")
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should output values for.")
parser.add_argument('--output-file', default="/tmp/label_values.dat", dest='output_file',
                    help="Data file to write output to.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "..", "workspace")

# Open output data file
with open(args.output_file, "w") as output:
    # Open spectrum libraries in turn
    for library in args.libraries:
        library_path = os_path.join(workspace, library)
        library_object = SpectrumLibrarySqlite(path=library_path, create=False)

        # Loop over objects in each spectrum library
        for item in library_object.search(continuum_normalised=1, SNR=250):
            metadata = library_object.get_metadata(ids=item['specId'])[0]

            for label in args.labels:
                output.write("{} ".format(metadata.get(label, "-")))
            output.write("\n")
