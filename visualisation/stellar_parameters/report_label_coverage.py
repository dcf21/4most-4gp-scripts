#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a training set and a test set, and see how well the Cannon can reproduce the stellar labels on the test
set of stars.
"""

import argparse
from os import path as os_path
import logging
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--test', required=True, dest='test_library',
                    help="Library of spectra over which to check label coverage.")
parser.add_argument('--label', dest='label',
                    default="[Fe/H]",
                    help="Label to check coverage of.")
parser.set_defaults(interpolate=False)
args = parser.parse_args()

logger.info("Checking label coverage with arguments <{}> <{}>".format(args.test_library,
                                                                      args.label))

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "..", "workspace")

# Open library we're going to test
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=args.test_library,
                                                workspace=workspace,
                                                extra_constraints={"continuum_normalised": 1}
                                                )
test_library, test_library_items = [spectra[i] for i in ("library", "items")]

# Load test set
test_library_ids = [i["specId"] for i in test_library_items]

# Test if metadata label is set on each spectrum in turn
spectrum_count = 0
metadata_found_count = 0
for index in range(len(test_library_ids)):
    test_spectrum_array = test_library.open(ids=test_library_ids[index])
    metadata = test_spectrum_array.get_metadata(0)
    if (args.label not in metadata) or (metadata[args.label] is None) or (not np.isfinite(metadata[args.label])):
        spectrum_count += 1
    else:
        spectrum_count += 1
        metadata_found_count += 1

print "Label {} is set on {:d} / {:d} spectra.".format(args.label, metadata_found_count, spectrum_count)
