#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take the APOKASC training set and test sets, and see how well the Cannon can reproduce APOGEE labels on a test
set of stars.
"""

import sys
from os import path as os_path
import logging
import json
from astropy.table import Table

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import CannonInstance

logger = logging.getLogger(__name__)

# Read input parameters
assert len(sys.argv) == 3, """Run this script with the command line syntax

python cannon_test.py <HRS|LRS> <output_path>"""

test_name = sys.argv[1]  # HRS or LRS
output_path = sys.argv[2]

# List of labels over which we are going to test the performance of the Cannon
test_labels = ("Teff", "logg", "[Fe/H]",
               "[C/H]", "[N/H]", "[O/H]", "[Na/H]", "[Mg/H]", "[Al/H]", "[Si/H]",
               "[Ca/H]", "[Ti/H]", "[Mn/H]", "[Co/H]", "[Ni/H]", "[Ba/H]", "[Sr/H]")

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "workspace")

# Open training set
training_library_name = "APOKASC_trainingset_{}".format(test_name)
training_library_path = os_path.join(workspace, training_library_name)
training_library = SpectrumLibrarySqlite(path=training_library_path, create=False)

# Open test set
test_library_name = "testset_{}".format(test_name)
test_library_path = os_path.join(workspace, test_library_name)
test_library = SpectrumLibrarySqlite(path=test_library_path, create=False)

# Load training set
training_library_ids = [i["specId"] for i in training_library.search()]
training_library = training_library.open(ids=training_library_ids)

# Load test set
test_library_ids = [i["specId"] for i in test_library.search()]

# Construct and train a model
model = CannonInstance(training_set=training_library, label_names=test_labels)

# Test the model
N = len(test_library_ids)
results = []
for index in range(N):
    test_library = test_library.open(ids=test_library_ids[index])
    spectrum = test_library.extract_item(0)
    star_name = spectrum.metadata["Starname"]
    print("Testing {}/{}: {}".format(index + 1, N, star_name))

    labels, cov, meta = model.fit_spectrum(spectrum=spectrum)

    # Identify which star it is and what the SNR is
    star_number = spectrum.metadata["star"]
    snr = spectrum.metadata["snr"]

    # From the label covariance matrix extract the standard deviation in each label value
    # (diagonal terms in the matrix are variances)
    err_labels = np.sqrt(np.diag(cov[0]))

    # Turn list of label values into a dictionary
    result = dict(zip(label_names, labels[0]))

    # Add the standard deviations of each label into the dictionary
    result.update(dict(zip(["E_{}".format(label_name) for label_name in label_names], err_labels)))

    # Add the APOGEE star number and the SNR ratio of the test spectrum
    result.update({"star": star_number, "snr": snr})
    results.append(result)

# Write results to a file
with open("{}.json".format(output_path), "w") as f:
    f.write(json.dumps(results))

results = Table(rows=results)
results.write("{}.fits".format(output_path))
