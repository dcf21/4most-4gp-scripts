#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take a library (or libraries) of spectra, and rearrange them. Either merge multiple libraries into one, split one
input library in multiple outputs, add contamination
"""

import argparse
import os
from os import path as os_path
import time
import re
import random
import logging

from fourgp_speclib import SpectrumLibrarySqlite
import fourgp_degrade

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-library',
                    action="append",
                    dest="input_library",
                    help="Specify the name of the SpectrumLibrary we are to read input spectra from.")
parser.add_argument('--output-library',
                    action="append",
                    dest="output_library",
                    help="Specify the name of the SpectrumLibrary we are to feed output into.")
parser.add_argument('--contamination-library',
                    action="append",
                    dest="contamination_library",
                    help="Contaminate output spectra with a randomly chosen spectrum from this library")
parser.add_argument('--contamination-fraction',
                    action="append",
                    dest="contamination_fraction",
                    help="Specify a fraction of photons which should come from contaminating sources.")
parser.add_argument('--output-fraction',
                    action="append",
                    dest="output_fraction",
                    help="If multiple output libraries are specified, the input spectra are randomly split between them. Specify the fraction to end up in each output library.")
parser.add_argument('--create',
                    required=False,
                    action='store_true',
                    dest="create",
                    help="Create a clean SpectrumLibrary to feed synthesized spectra into")
parser.add_argument('--no-create',
                    required=False,
                    action='store_false',
                    dest="create",
                    help="Do not create a clean SpectrumLibrary to feed synthesized spectra into")
parser.set_defaults(create=True)
parser.add_argument('--log-file',
                    required=False,
                    default="/tmp/rearrange_{}.log".format(pid),
                    dest="log_to",
                    help="Specify a log file where we log our progress.")
args = parser.parse_args()

logger.info("Running rearrange on spectra with arguments <{}> <{}> <{}>".format(args.input_library,
                                                                                args.output_library,
                                                                                args.contamination_library))

# Set path to workspace where we create libraries of spectra
workspace = os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))


# Helper for opening input SpectrumLibrary(s)
def open_input_libraries(inputs):
    if inputs is None:
        return []
    input_libraries = []
    for library_spec in inputs:
        test = re.match("(.*)\[(.*)\]", library_spec)
        constraints = {}
        if test is None:
            library_name = library_spec
        else:
            library_name = test.group(1)
            for constraint in test.group(2).split(","):
                words = constraint.split("=")
                assert len(words) == 2, "Could not parse constraint <{}>".format(constraint)
                constraint_name = words[0]
                constraint_value = words[1]
                try:
                    constraint_value = float(words[1])
                except ValueError:
                    pass
                constraints[constraint_name] = constraint_value
        constraints["continuum_normalised"] = 0  # All input spectra must not be continuum normalised
        library_path = os_path.join(workspace, library_name)
        input_library = SpectrumLibrarySqlite(path=library_path, create=False)
        if len(input_library.search()) == 0:
            continue
        library_items = input_library.search(**constraints)
        input_libraries.append({
            "library": input_library,
            "items": library_items
        })
    return input_libraries


def make_weighted_choice(weights):
    weights_sum = sum(weights)
    selected_index = 0
    output_select = random.uniform(a=0, b=weights_sum)
    for index, weight in enumerate(weights):
        output_select -= weight
        if output_select <= 0:
            selected_index = index
            break
    return selected_index


# Open input SpectrumLibrary(s)
input_libraries = open_input_libraries(args.input_library)

# Open contaminating SpectrumLibrary(s)
contamination_libraries = open_input_libraries(args.contamination_library)
contamination_spectra = []
for library in contamination_libraries:
    library_obj = library["library"]
    for item in library["items"]:
        contamination_spectrum = library_obj.open(ids=item['specId']).extract_item(0)

        # Look up the name of the star we've just loaded
        object_name = contamination_spectrum.metadata['Starname']

        # Search for the continuum-normalised version of this same object
        search_constraints = {
            "Starname": object_name,
            "continuum_normalised": 1
        }
        if "SNR" in contamination_spectrum.metadata:
            search_constraints["SNR"] = contamination_spectrum.metadata["SNR"]
        continuum_normalised_spectrum_id = library_obj.search(**search_constraints)

        # Check that continuum-normalised spectrum exists
        assert len(continuum_normalised_spectrum_id) == 1, "Could not find continuum-normalised spectrum."

        # Load the continuum-normalised version
        contamination_spectrum_continuum_normalised_arr = library_obj.open(
            ids=continuum_normalised_spectrum_id[0]['specId'])
        contamination_spectrum_continuum_normalised = contamination_spectrum_continuum_normalised_arr.extract_item(0)

        contamination_spectra.append(
            [contamination_spectrum, contamination_spectrum_continuum_normalised]
        )

# Create new SpectrumLibrary(s)
output_libraries = []
for library_name in args.output_library:
    library_path = os_path.join(workspace, library_name)
    output_libraries.append(SpectrumLibrarySqlite(path=library_path, create=args.create))

# Contamination fractions
contamination_fractions = []
if args.contamination_fraction is not None:
    contamination_fractions = [float(i) for i in args.contamination_fraction]
if len(contamination_fractions) == 0:
    contamination_fractions = [0]

# Output fractions
output_fractions = []
if args.output_fraction is not None:
    output_fractions = [float(i) for i in args.output_fraction]
if len(output_fractions) == 0:
    output_fractions = [1]
assert len(output_fractions) == len(output_libraries), "Must have an output fraction specified for each output library."

# Keep a record of which stars are being sent to which output
output_destinations = {}

# Loop over spectra to process
with open(args.log_to, "w") as result_log:
    for contamination_fraction in contamination_fractions:
        for input_library in input_libraries:
            library_obj = input_library["library"]
            for input_spectrum_id in input_library["items"]:
                logger.info("Working on <{}>".format(input_spectrum_id['filename']))

                # Open Spectrum data from disk
                input_spectrum_array = library_obj.open(ids=input_spectrum_id['specId'])
                input_spectrum = input_spectrum_array.extract_item(0)

                # Look up the name of the star we've just loaded
                object_name = input_spectrum.metadata['Starname']

                # Write log message
                result_log.write("\n[{}] {}".format(time.asctime(), object_name))
                result_log.flush()

                # Search for the continuum-normalised version of this same object
                search_constraints = {
                    "Starname": object_name,
                    "continuum_normalised": 1
                }
                if "SNR" in input_spectrum.metadata:
                    search_constraints["SNR"] = input_spectrum.metadata["SNR"]
                continuum_normalised_spectrum_id = library_obj.search(**search_constraints)

                # Check that continuum-normalised spectrum exists
                assert len(continuum_normalised_spectrum_id) == 1, "Could not find continuum-normalised spectrum."

                # Load the continuum-normalised version
                input_spectrum_continuum_normalised_arr = library_obj.open(
                    ids=continuum_normalised_spectrum_id[0]['specId'])
                input_spectrum_continuum_normalised = input_spectrum_continuum_normalised_arr.extract_item(0)

                # Contaminate this spectrum if requested
                if contamination_fraction > 0:
                    contamination_spectrum, contamination_spectrum_continuum_normalised = \
                        random.choice(contamination_spectra)

                    input_integral = input_spectrum.integral()
                    contamination_integral = contamination_spectrum.integral()

                    # Interpolate the contamination spectrum onto the observed spectrum's wavelength
                    interpolator = fourgp_degrade.SpectrumInterpolator(contamination_spectrum)
                    contamination_resampled = interpolator.match_to_other_spectrum(other=input_spectrum,
                                                                                   interpolate_errors=False,
                                                                                   interpolate_mask=False)

                    interpolator = fourgp_degrade.SpectrumInterpolator(contamination_spectrum_continuum_normalised)
                    contamination_cn_resampled = interpolator.match_to_other_spectrum(other=input_spectrum,
                                                                                      interpolate_errors=False,
                                                                                      interpolate_mask=False)

                    input_spectrum.values = \
                        (input_spectrum.values * (1 - contamination_fraction) +
                         contamination_resampled.values * contamination_fraction *
                         input_integral / contamination_integral)

                    input_spectrum_continuum_normalised.values = \
                        (input_spectrum_continuum_normalised.values * (1 - contamination_fraction) +
                         contamination_cn_resampled.values * contamination_fraction *
                         input_integral / contamination_integral)

                # Select which output library to send this spectrum to
                # Be sure to send all spectra relating to any particular star to the same destination
                if object_name in output_destinations:
                    output_index = output_destinations[object_name]
                else:
                    output_index = make_weighted_choice(output_fractions)
                    output_destinations[object_name] = output_index

                # Import spectra into output spectrum library
                output_libraries[output_index].insert(spectra=input_spectrum,
                                                      filenames=input_spectrum_id['filename'])

                output_libraries[output_index].insert(spectra=input_spectrum_continuum_normalised,
                                                      filenames=continuum_normalised_spectrum_id[0]['filename'])
