#!../../../../virtualenv/bin/python3
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
import gzip
import json
import logging
import os
import time
from os import path as os_path

import numpy as np
from fourgp_cannon import __version__ as fourgp_version
from fourgp_degrade import SpectrumProperties
from fourgp_speclib import SpectrumLibrarySqlite


def select_cannon(continuum_normalisation="none", cannon_version="casey_old"):
    """
    Select which Cannon wrapper to use, based on whether we've been asked to do continuum normalisation or not.

    :param continuum_normalisation:
        String indicating the name of the continuum normalisation scheme we've been asked to use. It is recommended
        to use "none", meaning that you've already done continuum normalisation.

    :param cannon_version:
        The name of the Cannon version to use. Must be one of "casey_old", "casey_new", "anna_ho".

    :return:
        A list of three items:

        1. A class which wraps the Cannon.
        2. Boolean flag indicating whether we want the training set already continuum normalised before input.
        3. Boolean flag indicating whether we want the test set already continuum normalised before input.
    """
    # Make sure that a valid version of the Cannon is selected
    assert cannon_version in ["casey_old", "casey_new", "anna_ho"]

    # We only import the Cannon inside this if statement, so that the user doesn't have to have all the Cannon
    # versions installed to use one of them.
    if cannon_version == "casey_old":
        from fourgp_cannon.cannon_wrapper_casey_old import \
            CannonInstanceCaseyOld, \
            CannonInstanceCaseyOldWithContinuumNormalisation, CannonInstanceCaseyOldWithRunningMeanNormalisation

        cannon_classes = {
            "vanilla": CannonInstanceCaseyOld,
            "automatic_continuum_normalisation": CannonInstanceCaseyOldWithContinuumNormalisation,
            "running_mean_normalisation": CannonInstanceCaseyOldWithRunningMeanNormalisation
        }

    elif cannon_version == "casey_new":
        from fourgp_cannon.cannon_wrapper_casey_new import \
            CannonInstanceCaseyNew, \
            CannonInstanceCaseyNewWithContinuumNormalisation, CannonInstanceCaseyNewWithRunningMeanNormalisation

        cannon_classes = {
            "vanilla": CannonInstanceCaseyNew,
            "automatic_continuum_normalisation": CannonInstanceCaseyNewWithContinuumNormalisation,
            "running_mean_normalisation": CannonInstanceCaseyNewWithRunningMeanNormalisation
        }

    elif cannon_version == "anna_ho":
        from fourgp_cannon.cannon_wrapper_anna_ho import CannonInstanceAnnaHo

        cannon_classes = {
            "vanilla": CannonInstanceAnnaHo,
            "automatic_continuum_normalisation": None,
            "running_mean_normalisation": None
        }

    else:
        assert False, "Unknown Cannon version <{}>".format(cannon_version)

    # Make sure that a valid continuum normalisation option is selected
    assert continuum_normalisation in ["none", "running_mean", "polynomial"]

    # Running mean normalisation. We accept flux-normalised spectra, and normalised each pixel by the mean flux in
    # a running window of pixels on either side of that pixel.
    if continuum_normalisation == "running_mean":
        cannon_class = cannon_classes["running_mean_normalisation"]
        continuum_normalised_training = False
        continuum_normalised_testing = False
    # Attempt to continuum normalise the spectra by fitting a polynomial to it. This implementation is really crude
    # and doesn't really manage to fit the continuum at all, so the results are a disaster.
    elif continuum_normalisation == "polynomial":
        cannon_class = cannon_classes["automatic_continuum_normalisation"]
        continuum_normalised_training = True
        continuum_normalised_testing = False
    # Assume that spectra have already been continuum normalised. You must use this option for now if you want
    # sensible results.
    else:
        cannon_class = cannon_classes["vanilla"]
        continuum_normalised_training = True
        continuum_normalised_testing = True
    return cannon_class, continuum_normalised_testing, continuum_normalised_training


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
    resampler = SpectrumResampler(input_spectrum=spectrum)
    spectrum_new = resampler.match_to_other_spectrum(other=first_training_spectrum)
    spectrum_new.metadata = spectrum.metadata
    return spectrum_new


def autocomplete_scaled_solar_abundances(training_library, training_library_ids_all, label_list):
    """
    Where stars have elemental abundances missing, insert scaled-solar values.

    :param training_library:
        SpectrumLibrary containing the spectra we are to train the Cannon on.
    :type training_library:
        SpectrumLibrarySqlite
    :param training_library_ids_all:
        List of the UIDs of the training spectra we are to use.
    :type training_library_ids_all:
        list
    :param label_list:
        The list of the labels which must be set on every spectrum.
    :return:
        A list of two items:

        0. A list of the IDs of the selected spectra
        1. A SpectrumArray of the selected spectra
    """
    input_spectra = training_library.open(ids=training_library_ids_all)

    for index in range(len(input_spectra)):
        metadata = input_spectra.get_metadata(index)
        for label in label_list:
            if (label not in metadata) or (metadata[label] is None) or (not np.isfinite(metadata[label])):
                # print "Label {} in spectrum {} assumed as scaled solar.".format(label, index)
                metadata[label] = metadata["[Fe/H]"]
    output_spectra = input_spectra

    return training_library_ids_all, output_spectra


def filter_training_spectra(training_library, training_library_ids_all, label_list):
    """
    Filter the spectra in a SpectrumArray on the basis that they must have a list of metadata values defined.

    :param training_library:
        SpectrumLibrary containing the spectra we are to train the Cannon on.
    :type training_library:
        SpectrumLibrarySqlite
    :param training_library_ids_all:
        List of the UIDs of the training spectra we are to use.
    :type training_library_ids_all:
        list
    :param label_list:
        The list of labels which must be set in order for a spectrum to be accepted.
    :return:
        A list of two items:

        0. A list of the IDs of the selected spectra
        1. A SpectrumArray of the selected spectra
    """
    input_spectra = training_library.get_metadata(ids=training_library_ids_all)

    ids_filtered = []
    for index, metadata in enumerate(input_spectra):
        accept = True
        for label in label_list:
            if (label not in metadata) or (metadata[label] is None) or (not np.isfinite(metadata[label])):
                accept = False
                break
        if accept:
            ids_filtered.append(training_library_ids_all[index])
    logging.info("Accepted {:d} / {:d} training spectra; others had labels missing.".
                 format(len(ids_filtered), len(training_library_ids_all)))
    output_spectrum_ids = ids_filtered
    output_spectra = training_library.open(ids=output_spectrum_ids)

    return output_spectrum_ids, output_spectra


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
        the Cannon is fitting can see all pixels relevant to all the labels we're fitting. The censoring is a simple
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
        A list of the labels the Cannon is fitting. Used to determine which elements we need to include lines for.
    :param label_expressions:
        A list of the algebraic expressions for any label expressions we're fitting.
    :return:
        A dictionary of Boolean masks, one for each label.
    """
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

            logging.info("Pixels used for label {}: {} of {} (in {} lines)".
                         format(label_name, mask.sum(), len(raster), allowed_lines))

            # Invert the mask because the Cannon expects pixels to be True when they are *excluded*
            censoring_masks[label_name] = ~mask

        # Make sure that label expressions also have masks set
        for label_name in label_expressions:
            mask = censoring_masks["Teff"].copy()
            censoring_masks[label_name] = mask

            logging.info("Pixels used for label {}: {} of {} (copied from Teff)".
                         format(label_name, len(raster) - mask.sum(), len(raster)))
    return censoring_masks


def main():
    """
    Main entry point for running the Cannon.
    """
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
    parser.add_argument('--train', required=False, dest='train_library', default=None,
                        help="Library of labelled spectra to train the Cannon on. Stars may be filtered by parameters "
                             "by placing a comma-separated list of constraints in [] brackets after the name of the "
                             "library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                             "range.")
    parser.add_argument('--workspace', dest='workspace', default="",
                        help="Directory where we expect to find spectrum libraries.")
    parser.add_argument('--cannon-version', default="casey_old", dest='cannon_version',
                        choices=("casey_old", "casey_new", "anna_ho"),
                        help="Select which implementation of the Cannon to use: Andy Casey's or Anna Ho's.")
    parser.add_argument('--polynomial-order', default=2, dest='polynomial_order', type=int,
                        help="The maximum order of polynomials to use as basis functions in the Cannon.")
    parser.add_argument('--continuum-normalisation', default="none", dest='continuum_normalisation',
                        help="Select continuum normalisation method: none, running_mean or polynomial.")
    parser.add_argument('--reload-cannon', required=False, dest='reload_cannon', default=None,
                        help="Skip training step, and reload a Cannon that we've previously trained. Specify the full "
                             "path to the .cannon file containing the trained Cannon, but without the .cannon suffix.")
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

    logging.info("Testing Cannon with arguments <{}> <{}> <{}> <{}>".format(args.test_library,
                                                                            args.train_library,
                                                                            args.censor_line_list,
                                                                            args.output_file))

    # Pick which Cannon version to use
    cannon_class, continuum_normalised_testing, continuum_normalised_training = \
        select_cannon(cannon_version=args.cannon_version,
                      continuum_normalisation=args.continuum_normalisation)

    # List of labels over which we are going to test the performance of the Cannon
    test_label_fields = args.labels.split(",")

    # List of labels we're going to fit individually
    if args.labels_individual:
        test_labels_individual = [i.split("+") for i in args.labels_individual.split(",")]
    else:
        test_labels_individual = [[]]

    # Set path to workspace where we expect to find libraries of spectra
    our_path = os_path.split(os_path.abspath(__file__))[0]
    workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

    # Find out whether we're reloading a previously saved Cannon
    reloading_cannon = args.reload_cannon is not None

    # Open training set
    training_library = training_library_ids_all = None
    if not reloading_cannon:
        spectra = SpectrumLibrarySqlite.open_and_search(
            library_spec=args.train_library,
            workspace=workspace,
            extra_constraints={"continuum_normalised": continuum_normalised_training}
        )
        training_library, training_library_items = [spectra[i] for i in ("library", "items")]

        # Make list of IDs of all spectra in the training set
        training_library_ids_all = [i["specId"] for i in training_library_items]

    # Open test set
    spectra = SpectrumLibrarySqlite.open_and_search(
        library_spec=args.test_library,
        workspace=workspace,
        extra_constraints={"continuum_normalised": continuum_normalised_testing}
    )
    test_library, test_library_items = [spectra[i] for i in ("library", "items")]

    # Make list of IDs of all spectra in the test set
    test_library_ids = [i["specId"] for i in test_library_items]

    # Fit each set of labels we're fitting individually, one by one
    for labels_individual_batch_count, test_labels_individual_batch in enumerate(test_labels_individual):

        # Create filename for the output from this Cannon run
        output_filename = args.output_file

        # If we're fitting elements individually, individually number the runs to fit each element
        if len(test_labels_individual) > 1:
            output_filename += "-{:03d}".format(labels_individual_batch_count)

        # Sequence of tasks if we're reloading a pre-saved Cannon from disk
        if reloading_cannon:

            # Load the JSON data that summarises the Cannon training that we're about to reload
            json_summary_filename = "{}.summary.json.gz".format(args.reload_cannon)
            cannon_pickle_filename = "{}.cannon".format(args.reload_cannon)

            with gzip.open(json_summary_filename, "rt") as f:
                summary_json = json.loads(f.read())

            raster = np.array(summary_json['wavelength_raster'])
            test_labels = summary_json['labels']
            training_library_ids = summary_json['training_spectra_ids']
            training_library_string = summary_json['train_library']
            assume_scaled_solar = summary_json['assume_scaled_solar']
            tolerance = summary_json['tolerance']
            line_list = summary_json['line_list']
            censoring_masks = None

            # If we're doing our own continuum normalisation, we need to treat each wavelength arm separately
            wavelength_arm_breaks = SpectrumProperties(raster).wavelength_arms()['break_points']

            time_training_start = time.time()
            model = cannon_class(training_set=None,
                                 wavelength_arms=wavelength_arm_breaks,
                                 load_from_file=cannon_pickle_filename,
                                 label_names=test_labels,
                                 tolerance=args.tolerance,
                                 polynomial_order=args.polynomial_order,
                                 censors=None,
                                 threads=None if args.multithread else 1
                                 )
            time_training_end = time.time()

        # Sequence of tasks if we're training a Cannon from scratch
        else:

            training_library_string = args.train_library
            assume_scaled_solar = args.assume_scaled_solar
            tolerance = args.tolerance
            line_list = args.censor_line_list

            # If requested, fill in any missing labels on the training set by assuming scaled-solar abundances
            if args.assume_scaled_solar:
                training_library_ids, training_spectra = autocomplete_scaled_solar_abundances(
                    training_library=training_library,
                    training_library_ids_all=training_library_ids_all,
                    label_list=test_label_fields + test_labels_individual_batch
                )

            # Otherwise we reject any training spectra which have incomplete labels
            else:
                training_library_ids, training_spectra = filter_training_spectra(
                    training_library=training_library,
                    training_library_ids_all=training_library_ids_all,
                    label_list=test_label_fields + test_labels_individual_batch
                )

            # Look up the raster on which the training spectra are sampled
            raster = training_spectra.wavelengths

            # Evaluate labels which are calculated via metadata expressions
            test_labels_expressions = []
            if args.label_expressions.strip():
                test_labels_expressions = args.label_expressions.split(",")
                evaluate_computed_labels(label_expressions=test_labels_expressions, spectra=training_spectra)

            # Make combined list of all labels the Cannon is going to fit
            test_labels = test_label_fields + test_labels_individual_batch + test_labels_expressions
            logging.info("Beginning fit of labels <{}>.".format(",".join(test_labels)))

            # If required, generate the censoring masks
            censoring_masks = create_censoring_masks(
                censoring_scheme=int(args.censor_scheme),
                raster=raster,
                censoring_line_list=args.censor_line_list,
                label_fields=test_label_fields + test_labels_individual_batch,
                label_expressions=test_labels_expressions
            )

            # If we're doing our own continuum normalisation, we need to treat each wavelength arm separately
            wavelength_arm_breaks = SpectrumProperties(raster).wavelength_arms()['break_points']

            # Construct and train a model
            time_training_start = time.time()
            model = cannon_class(training_set=training_spectra,
                                 wavelength_arms=wavelength_arm_breaks,
                                 label_names=test_labels,
                                 tolerance=args.tolerance,
                                 polynomial_order=args.polynomial_order,
                                 censors=censoring_masks,
                                 threads=None if args.multithread else 1
                                 )
            time_training_end = time.time()

            # Save the model
            model.save_model(filename="{:s}.cannon".format(output_filename),
                             overwrite=True)

        # Test the model
        N = len(test_library_ids)
        time_taken = np.zeros(N)
        results = []
        for index in range(N):
            test_spectrum_array = test_library.open(ids=test_library_ids[index])
            spectrum = test_spectrum_array.extract_item(0)
            logging.info("Testing {}/{}: {}".format(index + 1, N, spectrum.metadata['Starname']))

            # Calculate the time taken to process this spectrum
            time_start = time.time()

            # If requested, interpolate the test set onto the same raster as the training set. DANGEROUS!
            if args.interpolate:
                spectrum = resample_spectrum(spectrum=spectrum, training_spectra=training_spectra)

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
            uid = spectrum.metadata["uid"] if "uid" in spectrum.metadata else ""

            # From the label covariance matrix extract the standard deviation in each label value
            # (diagonal terms in the matrix are variances)
            if args.cannon_version == "anna_ho":
                err_labels = cov[0]
            else:
                err_labels = np.sqrt(np.diag(cov[0]))

            # Turn list of label values into a dictionary
            cannon_output = dict(list(zip(test_labels, labels[0])))

            # Add the standard deviations of each label into the dictionary
            cannon_output.update(dict(list(zip(["E_{}".format(label_name) for label_name in test_labels], err_labels))))

            # Add the star name and the SNR ratio of the test spectrum
            result = {"Starname": star_name,
                      "uid": uid,
                      "time": time_taken[index],
                      "spectrum_metadata": spectrum.metadata,
                      "cannon_output": cannon_output
                      }
            results.append(result)

        # Report time taken
        logging.info("Fitting of {:d} spectra completed. Took {:.2f} +/- {:.2f} sec / spectrum.".
                     format(N,
                            np.mean(time_taken),
                            np.std(time_taken)))

        # Create output data structure
        censoring_output = None
        if reloading_cannon:
            censoring_output = summary_json['censoring_mask']
        else:
            if censoring_masks is not None:
                censoring_output = dict([(label, tuple([int(i) for i in mask]))
                                         for label, mask in censoring_masks.items()])

        output_data = {
            "hostname": os.uname()[1],
            "generator": __file__,
            "4gp_version": fourgp_version,
            "cannon_version": model.cannon_version,
            "start_time": time_training_start,
            "end_time": time.time(),
            "training_time": time_training_end - time_training_start,
            "description": args.description,
            "train_library": training_library_string,
            "test_library": args.test_library,
            "training_spectra_ids": training_library_ids,
            "tolerance": tolerance,
            "assume_scaled_solar": assume_scaled_solar,
            "line_list": line_list,
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
