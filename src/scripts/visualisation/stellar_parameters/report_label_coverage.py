#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python report_label_coverage.py>, but <./report_label_coverage.py> will not work.

"""
Take a training set and a test set, and see how well the Cannon can reproduce the stellar labels on the test
set of stars.
"""

import argparse
from os import path as os_path

import numpy as np
from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Library of spectra over which to check label coverage. Stars may be filtered by parameters "
                         "by placing a comma-separated list of constraints in [] brackets after the name of the "
                         "library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                         "range.")
parser.add_argument('--label', dest='labels', action="append",
                    help="Label to check coverage of.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "../../../../workspace")

# Open library we're going to examine
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                workspace=workspace,
                                                extra_constraints={"continuum_normalised": 1}
                                                )
library, library_items = [spectra[i] for i in ("library", "items")]

# Fetch list of IDs of spectra in this library
library_ids = [i["specId"] for i in library_items]

# If user didn't specify which label(s) to fetch coverage for, fetch it for all labels
if args.labels is None:
    label_list = library.list_metadata_fields()
else:
    label_list = args.labels

# Create blank structure into which to count how many spectra have each label set
count = [0] * len(label_list)

# Test if metadata label is set on each spectrum in turn
spectrum_count = 0
for spectrum_index, spectrum_id in enumerate(library_ids):
    spectrum_array = library.open(ids=spectrum_id)
    spectrum_count += 1
    metadata = spectrum_array.get_metadata(0)

    for label_index, label in enumerate(label_list):
        if (label in metadata) and (metadata[label] is not None) and np.isfinite(metadata[label]):
            count[label_index] += 1

for label_index, label in enumerate(label_list):
    print("Label {:16s} is set on {:5d} / {:5d} spectra.".format(label, count[label_index], spectrum_count))
