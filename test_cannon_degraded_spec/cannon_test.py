#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take the APOKASC training set and test sets, and see how well the Cannon can reproduce APOGEE labels on a test
set of stars.
"""

import argparse
from os import path as os_path
import logging
import json
import time
import numpy as np
from astropy.table import Table
from astropy.io import fits

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import CannonInstance

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--test', required=True, dest='test_library')
parser.add_argument('--train', required=True, dest='train_library')
parser.add_argument('--censor', default="", dest='censor_line_list')
parser.add_argument('--output_file', default="./test_cannon.out", dest='output_file')
args = parser.parse_args()

logger.info("Testing Cannon with arguments <{}> <{}> <{}> <{}>".format(args.test_library,
                                                                       args.train_library,
                                                                       args.censor_line_list,
                                                                       args.output_file))

# List of labels over which we are going to test the performance of the Cannon
test_labels = ("Teff", "logg", "[Fe/H]",
               "[C/H]", "[N/H]", "[O/H]", "[Na/H]", "[Mg/H]", "[Al/H]", "[Si/H]",
               "[Ca/H]", "[Ti/H]", "[Mn/H]", "[Co/H]", "[Ni/H]", "[Ba/H]", "[Sr/H]")

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "workspace")

# Open training set
training_library_path = os_path.join(workspace, args.train_library)
training_library = SpectrumLibrarySqlite(path=training_library_path, create=False)

# Open test set
test_library_path = os_path.join(workspace, args.test_library)
test_library = SpectrumLibrarySqlite(path=test_library_path, create=False)

# Load training set
training_library_ids = [i["specId"] for i in training_library.search()]
training_spectra = training_library.open(ids=training_library_ids)
raster = training_spectra.wavelengths

# Load test set
test_library_ids = [i["specId"] for i in test_library.search()]

# If required, generate the censoring masks
censoring_masks = None
if args.censor_line_list != "":
    window = 0.5  # How many Angstroms either side of the line should be used?
    censoring_masks = {}
    ges_line_list = fits.open(args.censor_line_list)[1].data

    for label_name in test_labels[3:]:
        mask = np.zeros(raster.size, dtype=bool)

        # Find instances of this element in the line list
        element = label_name.lstrip("[").split("/")[0]
        match = np.any(ges_line_list["NAME"] == element, axis=1)

        # Get corresponding wavelengths
        matching_wavelengths = ges_line_list["LAMBDA"][match]

        # For each wavelength, allow +/- window that line.
        for i, wavelength in enumerate(matching_wavelengths):
            window_mask = ((wavelength + window) >= raster) * (raster >= (wavelength - window))
            mask[window_mask] = True

        logger.info("Pixels used for label {}: {} of {} (in {} lines)".format(label_name, mask.sum(),
                                                                              len(raster), len(matching_wavelengths)))
        censoring_masks[label_name] = ~mask

# Construct and train a model
model = CannonInstance(training_set=training_spectra, label_names=test_labels, censors=censoring_masks)

# Test the model
N = len(test_library_ids)
time_taken = np.zeros(N)
results = []
for index in range(N):
    test_spectrum_array = test_library.open(ids=test_library_ids[index])
    spectrum = test_spectrum_array.extract_item(0)
    star_name = spectrum.metadata["Starname"]
    # logger.info("Testing {}/{}: {}".format(index + 1, N, star_name))

    time_start = time.time()
    labels, cov, meta = model.fit_spectrum(spectrum=spectrum)
    time_end = time.time()
    time_taken[index] = time_end - time_start

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

# Report time taken
logger.info("Fitting of {:d} spectra completed. Took {:.2f} +/- {:.2f} sec / spectrum.".format(N,
                                                                                               np.mean(time_taken),
                                                                                               np.std(time_taken)))

# Write results to a file
with open(args.output_file + ".json", "w") as f:
    f.write(json.dumps(results))

results = Table(rows=results)
results.write(args.output_file + ".fits")
