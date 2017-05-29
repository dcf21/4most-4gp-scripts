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
import numpy as np
from astropy.table import Table
from astropy.io import fits

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import CannonInstance

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Read input parameters
assert len(sys.argv) == 4, """Run this script with the command line syntax

python cannon_test.py <HRS|LRS> <censor_name> <output_path>"""

test_name = sys.argv[1]  # <HRS> or <LRS>
censor_name = sys.argv[2]  # <lines_only> or <none>
output_path = sys.argv[3]

logger.info("Testing Cannon with arguments {} {} {}".format(test_name, censor_name, output_path))

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
training_spectra = training_library.open(ids=training_library_ids)
raster = training_spectra.wavelengths

# Load test set
test_library_ids = [i["specId"] for i in test_library.search()]

# If required, generate the censoring masks
censoring_masks = None
if censor_name == "lines_only":
    window = 0.5  # How many Angstroms either side of the line should be used?
    censoring_masks = {}
    ges_line_list = fits.open("ges_master_v5.fits")[1].data

    for label_name in test_labels[3:]:
        mask = np.zeros(raster.size, dtype=bool)

        # Find instances of this element in the line list
        element = label_name.lstrip("[").split("/")[0]
        match = np.any(ges_line_list["NAME"] == element, axis=1)

        # Get corresponding wavelengths
        matching_wavelengths = ges_line_list["LAMBDA"][match]

        # For each wavelength, allow +/- window that line.
        print("Found {} lines for {}".format(len(matching_wavelengths), label_name))

        for i, wavelength in enumerate(matching_wavelengths):
            window_mask = ((wavelength + window) >= raster) * (raster >= (wavelength - window))
            mask[window_mask] = True

        print("Pixels used for label {}: {} (of {})".format(label_name, mask.sum(), len(raster)))
        censoring_masks[label_name] = ~mask

# Construct and train a model
model = CannonInstance(training_set=training_spectra, label_names=test_labels, censors=censoring_masks)

# Test the model
N = len(test_library_ids)
results = []
for index in range(N):
    test_spectrum_array = test_library.open(ids=test_library_ids[index])
    spectrum = test_spectrum_array.extract_item(0)
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
    result = dict(zip(test_labels, labels[0]))

    # Add the standard deviations of each label into the dictionary
    result.update(dict(zip(["E_{}".format(label_name) for label_name in test_labels], err_labels)))

    # Add the APOGEE star number and the SNR ratio of the test spectrum
    result.update({"star": star_number, "snr": snr})
    results.append(result)

# Write results to a file
with open(os_path.join(output_path, "test_{}_{}.json".format(test_name, censor_name)), "w") as f:
    f.write(json.dumps(results))

results = Table(rows=results)
results.write(os_path.join(output_path, "test_{}_{}.fits".format(test_name, censor_name)).format(output_path))
