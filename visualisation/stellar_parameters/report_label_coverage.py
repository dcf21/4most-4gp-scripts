#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a training set and a test set, and see how well the Cannon can reproduce the stellar labels on the test
set of stars.
"""

import argparse
from os import path as os_path
import re
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


# Helper for opening input SpectrumLibrary(s)
def open_input_libraries(library_spec):
    test = re.match("([^\[]*)\[(.*)\]$", library_spec)
    constraints = {}
    if test is None:
        library_name = library_spec
    else:
        library_name = test.group(1)
        for constraint in test.group(2).split(","):
            words_1 = constraint.split("=")
            words_2 = constraint.split("<")
            if len(words_1) == 2:
                constraint_name = words_1[0]
                try:
                    constraint_value = float(words_1[1])
                except ValueError:
                    constraint_value = words_1[1]
                constraints[constraint_name] = constraint_value
            elif len(words_2) == 3:
                constraint_name = words_2[1]
                try:
                    constraint_value_a = float(words_2[0])
                    constraint_value_b = float(words_2[2])
                except ValueError:
                    constraint_value_a = words_2[0]
                    constraint_value_b = words_2[2]
                constraints[constraint_name] = (constraint_value_a, constraint_value_b)
            else:
                assert False, "Could not parse constraint <{}>".format(constraint)
    constraints["continuum_normalised"] = 1  # All input spectra must be continuum normalised
    library_path = os_path.join(workspace, library_name)
    input_library = SpectrumLibrarySqlite(path=library_path, create=False)
    library_items = input_library.search(**constraints)
    return {
        "library": input_library,
        "items": library_items
    }


# Open library we're going to test
spectra = open_input_libraries(args.test_library)
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
