#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python cannon_test.py>, but <./cannon_test.py> will not work.

"""
Take a training set and a test set, and see how well the Cannon can reproduce the stellar labels on the test
set of stars.

In theory, this code can be used on either continuum-normalised spectra, or non-continuum-normalised spectra. It uses
the metadata field "continuum_normalised" as a flag to determine which kind of spectrum has been supplied.

Note, however, that the continuum normalisation code is currently largely untested, so in practice you should always
pass this code continuum normalised spectra if you want scientifically meaningful results.

"""

import argparse
from os import path as os_path
import logging
import json
import time
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import \
    CannonInstance_2018_01_09, \
    CannonInstanceWithRunningMeanNormalisation_2018_01_09, \
    CannonInstanceWithContinuumNormalisation_2018_01_09


def select_cannon(continuum_normalisation):
    # Make sure that a valid continuum normalisation option is selected
    assert continuum_normalisation in ["none", "running_mean", "polynomial"]
    if continuum_normalisation == "running_mean":
        cannon_class = CannonInstanceWithRunningMeanNormalisation_2018_01_09
        continuum_normalised_training = False
        continuum_normalised_testing = False
    elif continuum_normalisation == "polynomial":
        cannon_class = CannonInstanceWithContinuumNormalisation_2018_01_09
        continuum_normalised_training = True
        continuum_normalised_testing = False
    else:
        # FIXME Use old Cannon for now, because the new Cannon produces worse fits
        cannon_class = CannonInstance_2018_01_09
        continuum_normalised_training = True
        continuum_normalised_testing = True
    return cannon_class, continuum_normalised_testing, continuum_normalised_training


def interpolate_spectrum(spectrum, training_spectra):
    from fourgp_degrade.interpolate import SpectrumInterpolator

    first_training_spectrum = training_spectra.extract_item(0)
    interpolator = SpectrumInterpolator(spectrum)
    spectrum_new = interpolator.match_to_other_spectrum(first_training_spectrum)
    spectrum_new.metadata = spectrum.metadata
    return spectrum_new


def autocomplete_scaled_solar_abundances(input_spectra, label_list, input_spectrum_ids):
    global logger
    for index in range(len(input_spectra)):
        metadata = input_spectra.get_metadata(index)
        for label in label_list:
            if (label not in metadata) or (metadata[label] is None) or (not np.isfinite(metadata[label])):
                # print "Label {} in spectrum {} assumed as scaled solar.".format(label, index)
                metadata[label] = metadata["[Fe/H]"]
    output_spectrum_ids = input_spectrum_ids
    output_spectra = input_spectra

    return output_spectrum_ids, output_spectra


def filter_training_spectra(input_spectra, label_list, input_library, input_spectrum_ids):
    global logger
    ids_filtered = []
    for index in range(len(input_spectra)):
        accept = True
        metadata = input_spectra.get_metadata(index)
        for label in label_list:
            if (label not in metadata) or (metadata[label] is None) or (not np.isfinite(metadata[label])):
                accept = False
                break
        if accept:
            ids_filtered.append(input_spectrum_ids[index])
    logger.info("Accepted {:d} / {:d} training spectra; others had labels missing.".
                format(len(ids_filtered), len(input_spectrum_ids)))
    output_spectrum_ids = ids_filtered
    output_spectra = input_library.open(ids=output_spectrum_ids)

    return output_spectrum_ids, output_spectra


def evaluate_computed_labels(label_expressions, spectra):
    global logger
    for index in range(len(spectra)):
        metadata = spectra.get_metadata(index)
        for label_expression in label_expressions:
            value = eval(label_expression, metadata)
            metadata[label_expression] = value


def create_censoring_masks(censoring_scheme, raster, censoring_line_list, label_fields, label_expressions):
    global logger
    censoring_masks = None
    if censoring_line_list != "":
        window = 1  # How many Angstroms either side of the line should be used?
        censoring_masks = {}
        line_list_txt = open(censoring_line_list).readlines()

        for label_name in label_fields:
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
                assert censoring_scheme in [1, 2, 3]
                if element_symbol != "H":

                    # Scheme 1: All elements can see all lines
                    if censoring_scheme == 1:
                        if "[{}/H]".format(element_symbol) not in label_fields:
                            continue

                    # Scheme 2: Elements can only see their own lines, but Teff, log(g) can see all
                    elif censoring_scheme == 2:
                        if label_name in ("Teff", "logg"):
                            if "[{}/H]".format(element_symbol) not in label_fields:
                                continue
                        else:
                            if "[{}/H]".format(element_symbol) != label_name:
                                continue

                    # Scheme 3: As scheme 2, but [Fe/H] can also see all
                    elif censoring_scheme == 3:
                        if label_name in ("Teff", "logg", "[Fe/H]"):
                            if "[{}/H]".format(element_symbol) not in label_fields:
                                continue
                        else:
                            if "[{}/H]".format(element_symbol) != label_name:
                                continue

                # Is line specified as a range (broad), or a single central wavelength (assume narrow)
                if "-" in wavelength:
                    pass_band = [float(i) for i in wavelength.split("-")]
                else:
                    pass_band = [float(wavelength) - window, float(wavelength) + window]

                # Allow this line
                allowed_lines += 1
                window_mask = (raster >= pass_band[0]) * (pass_band[1] >= raster)
                mask[window_mask] = True

            logger.info("Pixels used for label {}: {} of {} (in {} lines)".
                        format(label_name, mask.sum(), len(raster), allowed_lines))
            censoring_masks[label_name] = ~mask

        # Make sure that label expressions also have masks set
        for label_name in label_expressions:
            mask = censoring_masks["Teff"].copy()
            censoring_masks[label_name] = mask

            logger.info("Pixels used for label {}: {} of {} (copied from Teff)".
                        format(label_name, len(raster) - mask.sum(), len(raster)))
    return censoring_masks


def identify_wavelength_arms(raster):
    # We look at the wavelength raster of the first training spectrum, and look for break points
    break_points = []
    raster_diffs = np.diff(raster)
    diff = raster_diffs[0]
    for i in range(len(raster_diffs) - 2):
        second_diff = raster_diffs[i] / diff
        diff = raster_diffs[i]
        if (second_diff < 0.98) or (second_diff > 1.02):
            break_points.append((raster[i] + raster[i + 1]) / 2)
            diff = raster_diffs[i + 1]
    return break_points


def main():
    global logger

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', required=True, dest='test_library',
                        help="Library of spectra to test the trained Cannon on. Stars may be filtered by parameters by "
                             "placing a comma-separated list of constraints in [] brackets after the name of the "
                             "library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                             "range.")
    parser.add_argument('--train', required=True, dest='train_library',
                        help="Library of labelled spectra to train the Cannon on. Stars may be filtered by parameters "
                             "by placing a comma-separated list of constraints in [] brackets after the name of the "
                             "library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                             "range.")
    parser.add_argument('--workspace', dest='workspace', default="",
                        help="Directory where we expect to find spectrum libraries.")
    parser.add_argument('--continuum-normalisation', default="none", dest='continuum_normalisation',
                        help="Select continuum normalisation method: none, running_mean or polynomial.")
    parser.add_argument('--reload-cannon', required=False, dest='reload_cannon', default=None,
                        help="Skip training step, and reload a Cannon that we've previously trained.")
    parser.add_argument('--description', dest='description',
                        help="A description of this fitting run.")
    parser.add_argument('--labels', dest='labels',
                        default="Teff,logg,[Fe/H]",
                        help="List of the labels the Cannon is to learn to estimate.")
    parser.add_argument('--label-expressions', dest='label_expressions',
                        default="",
                        help="List of the algebraic labels the Cannon is to learn to estimate "
                             "(e.g. photometry_B - photometry_V).")
    parser.add_argument('--labels-individual', dest='labels_individual',
                        default="",
                        help="List of the labels the Cannon is to fit in separate fitting runs.")
    parser.add_argument('--censor-scheme', default="1", dest='censor_scheme',
                        help="Censoring scheme version to use (1, 2 or 3).")
    parser.add_argument('--censor', default="", dest='censor_line_list',
                        help="Optional list of line positions for the Cannon to fit, ignoring continuum between.")
    parser.add_argument('--tolerance', default=None, dest='tolerance', type=float,
                        help="The parameter xtol which is passed to the scipy optimisation routines as xtol to "
                             "determine whether they have converged.")
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
                        help="Do not assume scaled solar abundances; throw an error if training set is has missing "
                             "labels.")
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

    # Pick which Cannon version to use
    cannon_class, continuum_normalised_testing, continuum_normalised_training = \
        select_cannon(continuum_normalisation=args.continuum_normalisation)

    # List of labels over which we are going to test the performance of the Cannon
    test_label_fields = args.labels.split(",")

    # List of labels we're going to fit individually
    if args.labels_individual:
        test_labels_individual = [i.split("+") for i in args.labels_individual.split(",")]
    else:
        test_labels_individual = [[]]

    # Set path to workspace where we expect to find libraries of spectra
    our_path = os_path.split(os_path.abspath(__file__))[0]
    workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "workspace")

    # Open training set
    spectra = SpectrumLibrarySqlite.open_and_search(
        library_spec=args.train_library,
        workspace=workspace,
        extra_constraints={"continuum_normalised": continuum_normalised_training}
    )
    training_library, training_library_items = [spectra[i] for i in ("library", "items")]

    # Open test set
    spectra = SpectrumLibrarySqlite.open_and_search(
        library_spec=args.test_library,
        workspace=workspace,
        extra_constraints={"continuum_normalised": continuum_normalised_testing}
    )
    test_library, test_library_items = [spectra[i] for i in ("library", "items")]

    # Load training set
    training_library_ids_all = [i["specId"] for i in training_library_items]
    training_spectra_all = training_library.open(ids=training_library_ids_all)
    raster = training_spectra_all.wavelengths

    # Load test set
    test_library_ids = [i["specId"] for i in test_library_items]

    # Fit each set of labels we're fitting individually, one by one
    for labels_individual_batch_count, test_labels_individual_batch in enumerate(test_labels_individual):

        # If requested, fill in any missing labels on the training set by assuming scaled-solar abundances
        if args.assume_scaled_solar:
            training_library_ids, training_spectra = \
                autocomplete_scaled_solar_abundances(
                    input_spectra=training_spectra_all,
                    label_list=test_label_fields + test_labels_individual_batch,
                    input_spectrum_ids=training_library_ids_all
                )
        else:
            training_library_ids, training_spectra = \
                filter_training_spectra(
                    input_spectra=training_spectra_all,
                    label_list=test_label_fields + test_labels_individual_batch,
                    input_library=training_library,
                    input_spectrum_ids=training_library_ids_all
                )

        # Evaluate labels which are calculated via metadata expressions
        test_labels_expressions = []
        if args.label_expressions.strip():
            test_labels_expressions = args.label_expressions.split(",")
            evaluate_computed_labels(label_expressions=test_labels_expressions, spectra=training_spectra)

        # Make combined list of all labels the Cannon is going to fit
        test_labels = test_label_fields + test_labels_individual_batch + test_labels_expressions
        logger.info("Beginning fit of labels <{}>.".format(",".join(test_labels)))

        # If required, generate the censoring masks
        censoring_masks = create_censoring_masks(
            censoring_scheme=int(args.censor_scheme),
            raster=raster,
            censoring_line_list=args.censor_line_list,
            label_fields=test_label_fields + test_labels_individual_batch,
            label_expressions=test_labels_expressions
        )

        # If we're doing our own continuum normalisation, we need to treat each wavelength arm separately
        wavelength_arm_breaks = identify_wavelength_arms(raster=raster)

        # Construct and train a model
        time_training_start = time.time()
        if not args.reload_cannon:
            model = cannon_class(training_set=training_spectra,
                                 wavelength_arms=wavelength_arm_breaks,
                                 label_names=test_labels,
                                 tolerance=args.tolerance,
                                 censors=censoring_masks,
                                 threads=None if args.multithread else 1
                                 )
        else:
            model = cannon_class(training_set=training_spectra,
                                 wavelength_arms=wavelength_arm_breaks,
                                 load_from_file=args.reload_cannon,
                                 label_names=test_labels,
                                 tolerance=args.tolerance,
                                 censors=censoring_masks,
                                 threads=None if args.multithread else 1
                                 )
        time_training_end = time.time()

        # Save the model
        model.save_model(filename="{:s}-{:03d}.cannon".format(args.output_file, labels_individual_batch_count),
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
                spectrum = interpolate_spectrum(spectrum=spectrum, training_spectra=training_spectra)

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
            snr_per = spectrum.metadata["SNR_per"] if "SNR_per" in spectrum.metadata else "pixel"
            snr_definition = spectrum.metadata["snr_definition"] if "snr_definition" in spectrum.metadata else ""
            ebv = spectrum.metadata["e_bv"] if "e_bv" in spectrum.metadata else 0
            with_rv = spectrum.metadata["rv"] if "rv" in spectrum.metadata else 0
            uid = spectrum.metadata["uid"] if "uid" in spectrum.metadata else ""

            # From the label covariance matrix extract the standard deviation in each label value
            # (diagonal terms in the matrix are variances)
            err_labels = np.sqrt(np.diag(cov[0]))

            # Turn list of label values into a dictionary
            result = dict(zip(test_labels, labels[0]))

            # Add the standard deviations of each label into the dictionary
            result.update(dict(zip(["E_{}".format(label_name) for label_name in test_labels], err_labels)))

            # Add target values for each label into the dictionary
            for label_name in test_label_fields:
                if label_name in spectrum.metadata:
                    result["target_{}".format(label_name)] = spectrum.metadata[label_name]

            # Add the star name and the SNR ratio of the test spectrum
            result.update({"Starname": star_name,
                           "SNR": snr,
                           "SNR_per": snr_per,
                           "snr_definition": snr_definition,
                           "e_bv": ebv,
                           "rv": with_rv,
                           "uid": uid,
                           "time": time_taken[index]
                           })
            results.append(result)

        # Report time taken
        logger.info("Fitting of {:d} spectra completed. Took {:.2f} +/- {:.2f} sec / spectrum.".
                    format(N,
                           np.mean(time_taken),
                           np.std(time_taken)))

        # Write results to JSON file
        with open("{:s}-{:03d}.json".format(args.output_file, labels_individual_batch_count), "w") as f:
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


# Do it right away if we're run as a script
if __name__ == "__main__":
    main()