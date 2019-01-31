#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python payne_test.py>, but <./payne_test.py> will not work.

"""
Take a training set and a test set, and see how well the Payne can reproduce the stellar labels on the test
set of stars.

This code requires continuum normalised spectra.

"""

import argparse
import gzip
import json
import logging
import os
import time
from os import path as os_path

import numpy as np
from fourgp_payne import __version__ as fourgp_version
from fourgp_payne.payne_wrapper_ting import PayneInstanceTing
from fourgp_speclib import SpectrumLibrarySqlite


def resample_spectrum(spectrum, training_spectra):
    """
    Resample a test spectrum onto the same raster as the training spectra. This may be necessary if for some reason
    the test spectra are on a different raster, but it's not generally a good idea.

    :param spectrum:
        The test spectrum which is on a different raster to the training spectra.
    :param training_spectra:
        A sample training spectra, demonstrating the raster that the test spectrum needs to be on.
    :return:
        A resampled version of the test spectrum.
    """
    from fourgp_degrade.resample import SpectrumResampler

    first_training_spectrum = training_spectra.extract_item(0)
    resampler = SpectrumResampler(spectrum)
    spectrum_new = resampler.match_to_other_spectrum(first_training_spectrum)
    spectrum_new.metadata = spectrum.metadata
    return spectrum_new


def autocomplete_scaled_solar_abundances(input_spectra, label_list):
    """
    Where stars have elemental abundances missing, insert scaled-solar values.

    :param input_spectra:
        SpectrumArray containing the spectra we are to operate on.
    :param label_list:
        The list of the labels which must be set on every spectrum.
    :return:
        SpectrumArray with values filled in.
    """
    global logger
    for index in range(len(input_spectra)):
        metadata = input_spectra.get_metadata(index)
        for label in label_list:
            if (label not in metadata) or (metadata[label] is None) or (not np.isfinite(metadata[label])):
                # print "Label {} in spectrum {} assumed as scaled solar.".format(label, index)
                metadata[label] = metadata["[Fe/H]"]
    output_spectra = input_spectra

    return output_spectra


def filter_training_spectra(input_spectra, label_list, input_library, input_spectrum_ids):
    """
    Filter the spectra in a SpectrumArray on the basis that they must have a list of metadata values defined.

    :param input_spectra:
        A SpectrumArray from which we are to select spectra.
    :param label_list:
        The list of labels which must be set in order for a spectrum to be accepted.
    :param input_library:
        The input spectrum library from which these spectra were loaded (used to reload only the selected spectra).
    :param input_spectrum_ids:
        A list of the spectrum IDs of the spectra in the SpectrumArray <input_spectra>.
    :return:
        A list of two items:

        0. A list of the IDs of the selected spectra
        1. A SpectrumArray of the selected spectra
    """
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

    return output_spectra


def evaluate_computed_labels(label_expressions, spectra):
    """
    Evaluated computed labels for a spectrum. These are labels that are computed from multiple metadata items, such as
    B-V colours.

    :param label_expressions:
        A list of the computed label expressions that we are to evaluate for each spectrum.
    :param spectra:
        A SpectrumArray of the spectra for which we are to compute each computed label. The computed labels are added
        to the metadata dictionary for each spectrum.
    :return:
        None
    """
    global logger
    for index in range(len(spectra)):
        metadata = spectra.get_metadata(index)
        for label_expression in label_expressions:
            value = eval(label_expression, metadata)
            metadata[label_expression] = value


def create_censoring_masks(censoring_scheme, raster, censoring_line_list, label_fields, label_expressions):
    """
    Create censoring masks for each label we are fitting, based on pixels around the lines of each element.

    :param censoring_scheme:
        Switch to specify how censoring is done. There are three options: 1, 2 or 3. In Scheme 1, all of the labels
        the Payne is fitting can see all pixels relevant to all the labels we're fitting. The censoring is a simple
        mask, which is the same for all labels. In Scheme 2, each individual element can only see its own lines, but
        Teff and log(g) can see all of the pixels used by at least one of the individual elements. Scheme 3 is similar,
        but [Fe/H] is treated like Teff and log(g) and can see all the pixels used by at least one of the elements being
        fitting.

        For best results, use scheme 1.
    :param raster:
        The wavelength raster of the spectra we are fitting.
    :param censoring_line_list:
        The filename of the file with the line list we use create the censoring masks.
    :param label_fields:
        A list of the labels the Payne is fitting. Used to determine which elements we need to include lines for.
    :param label_expressions:
        A list of the algebraic expressions for any label expressions we're fitting.
    :return:
        A dictionary of Boolean masks, one for each label.
    """
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

                # We deal with excluded regions below; in this pass we put lines INTO the mask
                if element_symbol == "exclude":
                    continue

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

            # Loop over the excluded regions in the line list, and make sure they are not in the mask
            for line in line_list_txt:
                line = line.strip()

                # Ignore comment lines
                if (len(line) == 0) or (line[0] == "#"):
                    continue
                words = line.split()
                if words[0] == "exclude":
                    wavelength = words[1]
                    if "-" in wavelength:
                        pass_band = [float(i) for i in wavelength.split("-")]
                    else:
                        pass_band = [float(wavelength) - window, float(wavelength) + window]

                    # Disallow this region
                    window_mask = (raster >= pass_band[0]) * (pass_band[1] >= raster)
                    mask[window_mask] = False

            logger.info("Pixels used for label {}: {} of {} (in {} lines)".
                        format(label_name, mask.sum(), len(raster), allowed_lines))

            # Invert the mask because the Cannon expects pixels to be True when they are *excluded*
            censoring_masks[label_name] = ~mask

        # Make sure that label expressions also have masks set
        for label_name in label_expressions:
            mask = censoring_masks["Teff"].copy()
            censoring_masks[label_name] = mask

            logger.info("Pixels used for label {}: {} of {} (copied from Teff)".
                        format(label_name, len(raster) - mask.sum(), len(raster)))
    return censoring_masks


def main():
    """
    Main entry point for running the Payne.
    """
    global logger

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', required=True, dest='test_library',
                        help="Library of spectra to test the trained Payne on. Stars may be filtered by parameters by "
                             "placing a comma-separated list of constraints in [] brackets after the name of the "
                             "library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                             "range.")
    parser.add_argument('--train', required=True, dest='train_library',
                        help="Library of labelled spectra to train the Payne on. Stars may be filtered by parameters "
                             "by placing a comma-separated list of constraints in [] brackets after the name of the "
                             "library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                             "range.")
    parser.add_argument('--workspace', dest='workspace', default="",
                        help="Directory where we expect to find spectrum libraries.")
    parser.add_argument('--train-batch-number', required=False, dest='batch_number', type=int, default=0,
                        help="If training pixels in multiple batches on different machines, then this is the number of "
                             "the batch of pixels we are to train. It should be in the range 0 .. batch_count-1 "
                             "inclusive. If it is -1, then we skip training to move straight to testing.")
    parser.add_argument('--train-batch-count', required=False, dest='batch_count', type=int, default=1,
                        help="If training pixels in multiple batches on different machines, then this is the number "
                             "of batches.")
    parser.add_argument('--description', dest='description',
                        help="A description of this fitting run.")
    parser.add_argument('--labels', dest='labels',
                        default="Teff,logg,[Fe/H]",
                        help="List of the labels the Payne is to learn to estimate.")
    parser.add_argument('--label-expressions', dest='label_expressions',
                        default="",
                        help="List of the algebraic labels the Payne is to learn to estimate "
                             "(e.g. photometry_B - photometry_V).")
    parser.add_argument('--labels-individual', dest='labels_individual',
                        default="",
                        help="List of the labels the Payne is to fit in separate fitting runs.")
    parser.add_argument('--censor-scheme', default="1", dest='censor_scheme',
                        help="Censoring scheme version to use (1, 2 or 3).")
    parser.add_argument('--censor', default="", dest='censor_line_list',
                        help="Optional list of line positions for the Payne to fit, ignoring continuum between.")
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
                        help="Use multiple thread to speed Payne up.")
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

    logger.info("Testing Payne with arguments <{}> <{}> <{}> <{}>".format(args.test_library,
                                                                          args.train_library,
                                                                          args.censor_line_list,
                                                                          args.output_file))

    # List of labels over which we are going to test the performance of the Payne
    test_label_fields = args.labels.split(",")

    # List of labels we're going to fit individually
    if args.labels_individual:
        test_labels_individual = [i.split("+") for i in args.labels_individual.split(",")]
    else:
        test_labels_individual = [[]]

    # Set path to workspace where we expect to find libraries of spectra
    our_path = os_path.split(os_path.abspath(__file__))[0]
    workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

    # Open training set
    spectra = SpectrumLibrarySqlite.open_and_search(
        library_spec=args.train_library,
        workspace=workspace,
        extra_constraints={"continuum_normalised": True}
    )
    training_library, training_library_items = [spectra[i] for i in ("library", "items")]

    # Open test set
    spectra = SpectrumLibrarySqlite.open_and_search(
        library_spec=args.test_library,
        workspace=workspace,
        extra_constraints={"continuum_normalised": True}
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

        # Create filename for the output from this Payne run
        output_filename = args.output_file
        # If we're fitting elements individually, individually number the runs to fit each element
        if len(test_labels_individual) > 1:
            output_filename += "-{:03d}".format(labels_individual_batch_count)

        # If requested, fill in any missing labels on the training set by assuming scaled-solar abundances
        if args.assume_scaled_solar:
            training_spectra = autocomplete_scaled_solar_abundances(
                input_spectra=training_spectra_all,
                label_list=test_label_fields + test_labels_individual_batch
            )
        else:
            training_spectra = filter_training_spectra(
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

        # Make combined list of all labels the Payne is going to fit
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

        # Construct and train a model
        time_training_start = time.time()

        model = PayneInstanceTing(training_set=training_spectra,
                                  label_names=test_labels,
                                  batch_number=args.batch_number,
                                  batch_count=args.batch_count,
                                  censors=censoring_masks,
                                  threads=None if args.multithread else 1,
                                  training_data_archive=output_filename
                                  )

        time_training_end = time.time()

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
                spectrum = resample_spectrum(spectrum=spectrum, training_spectra=training_spectra)

            # Pass spectrum to the Payne
            fit_data = model.fit_spectrum(spectrum=spectrum)

            # Check whether Payne failed
            # if labels is None:
            #    continue

            # Measure the time taken
            time_end = time.time()
            time_taken[index] = time_end - time_start

            # Identify which star it is and what the SNR is
            star_name = spectrum.metadata["Starname"] if "Starname" in spectrum.metadata else ""
            uid = spectrum.metadata["uid"] if "uid" in spectrum.metadata else ""

            # Fudge the errors for now until I work this out
            err_labels = [0 for item in test_labels]

            # Turn list of label values into a dictionary
            payne_output = dict(list(zip(test_labels, fit_data['results'][0])))

            # Add the standard deviations of each label into the dictionary
            payne_output.update(dict(list(zip(["E_{}".format(label_name) for label_name in test_labels], err_labels))))

            # Add the star name and the SNR ratio of the test spectrum
            result = {"Starname": star_name,
                      "uid": uid,
                      "time": time_taken[index],
                      "spectrum_metadata": spectrum.metadata,
                      "cannon_output": payne_output
                      }
            results.append(result)

        # Report time taken
        logger.info("Fitting of {:d} spectra completed. Took {:.2f} +/- {:.2f} sec / spectrum.".
                    format(N,
                           np.mean(time_taken),
                           np.std(time_taken)))

        # Create output data structure
        censoring_output = None
        if censoring_masks is not None:
            censoring_output = dict([(label, tuple([int(i) for i in mask]))
                                     for label, mask in censoring_masks.items()])

        output_data = {
            "hostname": os.uname()[1],
            "generator": __file__,
            "4gp_version": fourgp_version,
            "cannon_version": None,
            "payne_version": model.payne_version,
            "start_time": time_training_start,
            "end_time": time.time(),
            "training_time": time_training_end - time_training_start,
            "description": args.description,
            "train_library": args.train_library,
            "test_library": args.test_library,
            "tolerance": None,
            "assume_scaled_solar": args.assume_scaled_solar,
            "line_list": args.censor_line_list,
            "labels": test_labels,
            "wavelength_raster": tuple(raster),
            "censoring_mask": censoring_output
        }

        # Write brief summary of run to JSON file, without masses of data
        with gzip.open("{:s}.summary.json.gz".format(output_filename), "wt") as f:
            f.write(json.dumps(output_data, indent=2))

        # Write full results to JSON file
        output_data["spectra"] = results
        with gzip.open("{:s}.full.json.gz".format(output_filename), "wt") as f:
            f.write(json.dumps(output_data, indent=2))


# Do it right away if we're run as a script
if __name__ == "__main__":
    main()
