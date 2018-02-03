#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take a training set and a test set, and see how well the Cannon can reproduce the stellar labels on the test
set of stars.

In theory, this code can be used on either continuum-normalised spectra, or non-continuum-normalised spectra. It uses
the metadata field "continuum_normalised" as a flag to determine which kind of spectrum has been supplied.

Note, however, that the continuum normalisation code is currently very dodgy, so in practice you should always
pass this code continuum normalised spectra if you want scientifically meaningful results.

"""

import argparse
from os import path as os_path
import re
import logging
import json
import time
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import \
    CannonInstance, \
    CannonInstanceWithRunningMeanNormalisation, \
    CannonInstanceWithContinuumNormalisation

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--test', required=True, dest='test_library',
                    help="Library of spectra to test the trained Cannon on.")
parser.add_argument('--train', required=True, dest='train_library',
                    help="Library of labelled spectra to train the Cannon on.")
parser.add_argument('--continuum-normalisation', default="none", dest='continuum_normalisation',
                    help="Select continuum normalisation method: none, running_mean or polynomial.")
parser.add_argument('--reload-cannon', required=False, dest='reload_cannon', default=None,
                    help="Skip training step, and reload a Cannon that we've previously trained.")
parser.add_argument('--description', dest='description',
                    help="A description of this fitting run.")
parser.add_argument('--labels', dest='labels',
                    default="Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H],[Ti/H],"
                            "[Mn/H],[Co/H],[Ni/H],[Ba/H],[Sr/H]",
                    help="List of the labels the Cannon is to learn to estimate.")
parser.add_argument('--censor', default="", dest='censor_line_list',
                    help="Optional list of line positions for the Cannon to fit, ignoring continuum between.")
parser.add_argument('--tolerance', default=1e-4, dest='tolerance', type=float,
                    help="The parameter xtol which is passed to the scipy optimisation routines as xtol to determine "
                         "whether they have converged.")
parser.add_argument('--output-file', default="./test_cannon.out", dest='output_file',
                    help="Data file to write output to.")
parser.add_argument('--assume-scaled-solar',
                    action='store_true',
                    dest="assume_scaled_solar",
                    help="Assume scaled solar abundances for any elements which don't have abundances individually "
                         "specified. Useful for working with incomplete data sets.")
parser.add_argument('--no-assume-scaled-solar',
                    action='store_false',
                    dest="assume_scaled_solar",
                    help="Do not assume scaled solar abundances; throw an error if training set is has missing labels.")
parser.set_defaults(assume_scaled_solar=False)
parser.add_argument('--multithread',
                    action='store_true',
                    dest="multithread",
                    help="Use multiple thread to speed Cannon up.")
parser.add_argument('--nothread',
                    action='store_false',
                    dest="multithread",
                    help="Do not use multiple threads - use only one CPU core.")
parser.set_defaults(multithread=True)
parser.add_argument('--interpolate',
                    action='store_true',
                    dest="interpolate",
                    help="Interpolate the test spectra on the training spectra's wavelength raster. DANGEROUS!")
parser.add_argument('--nointerpolate',
                    action='store_false',
                    dest="interpolate",
                    help="Do not interpolate the test spectra onto a different raster.")
parser.set_defaults(interpolate=False)
args = parser.parse_args()

logger.info("Testing Cannon with arguments <{}> <{}> <{}> <{}>".format(args.test_library,
                                                                       args.train_library,
                                                                       args.censor_line_list,
                                                                       args.output_file))

# Make sure that a valid continuum normalisation option is selected
assert args.continuum_normalisation in ["none", "running_mean", "polynomial"]

if args.continuum_normalisation == "running_mean":
    CannonClass = CannonInstanceWithRunningMeanNormalisation
    continuum_normalised_training = False
    continuum_normalised_testing = False
elif args.continuum_normalisation == "polynomial":
    CannonClass = CannonInstanceWithContinuumNormalisation
    continuum_normalised_training = True
    continuum_normalised_testing = False
else:
    CannonClass = CannonInstance
    continuum_normalised_training = True
    continuum_normalised_testing = True

# List of labels over which we are going to test the performance of the Cannon
test_labels = args.labels.split(",")

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "workspace")


# Helper for opening input SpectrumLibrary(s)
def open_input_libraries(library_spec, need_continuum_normalised):
    test = re.match("([^\[]*)\[(.*)\]$", library_spec)
    constraints = {"continuum_normalised": need_continuum_normalised}
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
    library_path = os_path.join(workspace, library_name)
    input_library = SpectrumLibrarySqlite(path=library_path, create=False)
    library_items = input_library.search(**constraints)
    return {
        "library": input_library,
        "items": library_items
    }


# Open training set
spectra = open_input_libraries(library_spec=args.train_library,
                               need_continuum_normalised=continuum_normalised_training)
training_library, training_library_items = [spectra[i] for i in ("library", "items")]

# Open test set
spectra = open_input_libraries(library_spec=args.test_library,
                               need_continuum_normalised=continuum_normalised_testing)
test_library, test_library_items = [spectra[i] for i in ("library", "items")]

# Load training set
training_library_ids = [i["specId"] for i in training_library_items]
training_spectra = training_library.open(ids=training_library_ids)
raster = training_spectra.wavelengths

# Load test set
test_library_ids = [i["specId"] for i in test_library_items]

# If requested, fill in any missing labels on the training set by assuming scaled-solar abundances
if args.assume_scaled_solar:
    for index in range(len(training_spectra)):
        metadata = training_spectra.get_metadata(index)
        for label in test_labels:
            if (label not in metadata) or (metadata[label] is None) or (not np.isfinite(metadata[label])):
                # print "Label {} in spectrum {} assumed as scaled solar.".format(label, index)
                metadata[label] = metadata["[Fe/H]"]
else:
    training_library_ids_filtered = []
    for index in range(len(training_spectra)):
        accept = True
        metadata = training_spectra.get_metadata(index)
        for label in test_labels:
            if (label not in metadata) or (metadata[label] is None) or (not np.isfinite(metadata[label])):
                accept = False
                break
        if accept:
            training_library_ids_filtered.append(training_library_ids[index])
    logger.info("Accepted {:d} / {:d} training spectra; others had labels missing.".
                format(len(training_library_ids_filtered), len(training_library_ids)))
    training_library_ids = training_library_ids_filtered
    training_spectra = training_library.open(ids=training_library_ids)

# If required, generate the censoring masks
censoring_masks = None
if args.censor_line_list != "":
    window = 1  # How many Angstroms either side of the line should be used?
    censoring_masks = {}
    line_list_txt = open(args.censor_line_list).readlines()

    for label_name in test_labels:
        allowed_lines = 0
        mask = np.zeros(raster.size, dtype=bool)

        # Loop over the lines in the line list and see which ones to include
        for line in line_list_txt:
            line = line.strip()

            # Ignore comment lines
            if (len(line) == 0) or (line[0] == "#"):
                continue
            words = line.split()
            element_symbol = words[0]
            wavelength = words[2]

            # Only select lines from elements we're trying to fit. Always use H lines.
            censoring_scheme = 1  # Because schemes 2 and 3 are a disaster
            if element_symbol != "H":
                if censoring_scheme == 1:  # All elements can see all lines
                    if "[{}/H]".format(element_symbol) not in test_labels:
                        continue
                elif censoring_scheme == 2:  # Elements can only see their own lines, but Teff, log(g) can see all
                    if label_name in ("Teff", "logg"):
                        if "[{}/H]".format(element_symbol) not in test_labels:
                            continue
                    else:
                        if "[{}/H]".format(element_symbol) != label_name:
                            continue
                elif censoring_scheme == 3:  # As scheme 2, but [Fe/H] can also see all
                    if label_name in ("Teff", "logg", "[Fe/H]"):
                        if "[{}/H]".format(element_symbol) not in test_labels:
                            continue
                    else:
                        if "[{}/H]".format(element_symbol) != label_name:
                            continue

            # Is line specified as a range (broad), or a single central wavelength (assume narrow)
            if "-" in wavelength:
                passband = [float(i) for i in wavelength.split("-")]
            else:
                passband = [float(wavelength) - window, float(wavelength) + window]

            # Allow this line
            allowed_lines += 1
            window_mask = (raster >= passband[0]) * (passband[1] >= raster)
            mask[window_mask] = True

        logger.info("Pixels used for label {}: {} of {} (in {} lines)".format(label_name, mask.sum(),
                                                                              len(raster), allowed_lines))
        censoring_masks[label_name] = ~mask

# If we're doing our own continuum normalisation, we need to treat each wavelength arm separately
# We look at the wavelength raster of the first training spectrum, and look for break points
spectrum = training_spectra.extract_item(0)
break_points = []
raster_diffs = np.diff(spectrum.wavelengths)
diff = raster_diffs[0]
for i in range(len(raster_diffs) - 2):
    second_diff = raster_diffs[i] / diff
    diff = raster_diffs[i]
    if (second_diff < 0.99) or (second_diff > 1.01):
        break_points.append((raster[i] + raster[i + 1]) / 2)
        diff = raster_diffs[i + 1]

# Construct and train a model
time_training_start = time.time()
if not args.reload_cannon:
    model = CannonClass(training_set=training_spectra,
                        wavelength_arms=break_points,
                           label_names=test_labels,
                           tolerance=args.tolerance,
                           censors=censoring_masks,
                           threads=None if args.multithread else 1
                           )
else:
    model = CannonClass(training_set=training_spectra,
                        wavelength_arms=break_points,
                           load_from_file=args.reload_cannon,
                           label_names=test_labels,
                           tolerance=args.tolerance,
                           censors=censoring_masks,
                           threads=None if args.multithread else 1
                           )
time_training_end = time.time()

# Save the model
model.save_model(filename=args.output_file + ".cannon",
                 overwrite=True)

# Test the model
N = len(test_library_ids)
time_taken = np.zeros(N)
results = []
for index in range(N):
    test_spectrum_array = test_library.open(ids=test_library_ids[index])
    spectrum = test_spectrum_array.extract_item(0)
    logger.info("Testing {}/{}: {}".format(index + 1, N, spectrum.metadata['Starname']))

    # Calculate the time taken to process this spectrum
    time_start = time.time()

    # If requested, interpolate the test set onto the same raster as the training set. DANGEROUS!
    if args.interpolate:
        from fourgp_degrade.interpolate import SpectrumInterpolator

        first_training_spectrum = training_spectra.extract_item(0)
        interpolator = SpectrumInterpolator(spectrum)
        spectrum_new = interpolator.match_to_other_spectrum(first_training_spectrum)
        spectrum_new.metadata = spectrum.metadata
        spectrum = spectrum_new

    # Pass spectrum to the Cannon
    labels, cov, meta = model.fit_spectrum(spectrum=spectrum)

    # Check whether Cannon failed
    if labels is None:
        continue

    # Measure the time taken
    time_end = time.time()
    time_taken[index] = time_end - time_start

    # Identify which star it is and what the SNR is
    star_name = spectrum.metadata["Starname"] if "Starname" in spectrum.metadata else ""
    snr = spectrum.metadata["SNR"] if "SNR" in spectrum.metadata else 0
    ebv = spectrum.metadata["e_bv"] if "e_bv" in spectrum.metadata else 0
    uid = spectrum.metadata["uid"] if "uid" in spectrum.metadata else ""

    # From the label covariance matrix extract the standard deviation in each label value
    # (diagonal terms in the matrix are variances)
    err_labels = np.sqrt(np.diag(cov[0]))

    # Turn list of label values into a dictionary
    result = dict(zip(test_labels, labels[0]))

    # Add the standard deviations of each label into the dictionary
    result.update(dict(zip(["E_{}".format(label_name) for label_name in test_labels], err_labels)))

    # Add target values for each label into the dictionary
    for label_name in test_labels:
        if label_name in spectrum.metadata:
            result["target_{}".format(label_name)] = spectrum.metadata[label_name]

    # Add the star name and the SNR ratio of the test spectrum
    result.update({"Starname": star_name, "SNR": snr, "e_bv": ebv, "uid":uid, "time": time_taken[index]})
    results.append(result)

# Report time taken
logger.info("Fitting of {:d} spectra completed. Took {:.2f} +/- {:.2f} sec / spectrum.".format(N,
                                                                                               np.mean(time_taken),
                                                                                               np.std(time_taken)))

# Write results to JSON file
with open(args.output_file + ".json", "w") as f:
    censoring_output = None
    if censoring_masks is not None:
        censoring_output = dict([(label, tuple([int(i) for i in mask]))
                                 for label, mask in censoring_masks.iteritems()])

    f.write(json.dumps({
        "train_library": args.train_library,
        "test_library": args.test_library,
        "tolerance": args.tolerance,
        "description": args.description,
        "assume_scaled_solar": args.assume_scaled_solar,
        "line_list": args.censor_line_list,
        "start_time": time_training_start,
        "end_time": time.time(),
        "training_time": time_training_end - time_training_start,
        "labels": test_labels,
        "wavelength_raster": tuple(raster),
        "censoring_mask": censoring_output,
        "stars": results
    }))