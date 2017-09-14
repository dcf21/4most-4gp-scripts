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
import logging

from fourgp_speclib import SpectrumLibrarySqlite

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
                    default="tmp_merged_output",
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
    input_libraries = []
    for library_spec in inputs:
        test = re.match("(.*)\[(.*)\]", library_spec)
        constraints = {}
        if test is None:
            library_name = library_spec
        else
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
        library_path = os_path.join(workspace, library_name)
        input_library = SpectrumLibrarySqlite(path=library_path, create=False)
        library_items = input_library.search(**constraints)
        input_libraries.append({
            "library": input_library,
            "items": library_items
        })
    return input_libraries


# Open input SpectrumLibrary(s)
input_libraries = open_input_libraries(args.input_library)

# Open contaminating SpectrumLibrary(s)
contamination_libraries = open_input_libraries(args.contamination_library)

# Create new SpectrumLibrary(s)
output_libraries = []
for library_name in args.output_library:
    library_path = os_path.join(workspace, library_name)
    output_libraries.append(SpectrumLibrarySqlite(path=library_path, create=args.create))

# Contamination fractions
contamination_fractions = [float(i) for i in args.contamination_fraction]

# Output fractions
output_fractions = [float(i) for i in args.output_fraction]
if len(output_fractions) == 0:
    output_fractions = [1]
assert len(output_fractions) == len(output_libraries), "Must have an output fraction specified for each output library."

# Loop over spectra to process
with open(args.log_to, "w") as result_log:
    for input_library in input_libraries:
        library_obj = input_library["library"]
        for input_spectrum in input_library["items"]:
            logger.info("Working on <{}>".format(input_spectrum['filename']))
            # Open Spectrum data from disk
            input_spectrum_array = library_obj.open(ids=input_spectrum['specId'])
            input_spectrum = input_spectrum_array.extract_item(0)

            # Look up the name of the star we've just loaded
            object_name = input_spectrum.metadata['Starname']

            # Write log message
            result_log.write("\n[{}] {}... ".format(time.asctime(), object_name))
            result_log.flush()

            # Search for the continuum-normalised version of this same object
            continuum_normalised_spectrum_id = input_library.search(Starname=object_name, continuum_normalised=1)

            # Check that continuum-normalised spectrum exists
            assert len(continuum_normalised_spectrum_id) == 1, "Could not find continuum-normalised spectrum."

            # Load the continuum-normalised version
            input_spectrum_continuum_normalised_arr = input_library.open(
                ids=continuum_normalised_spectrum_id[0]['specId'])
            input_spectrum_continuum_normalised = input_spectrum_continuum_normalised_arr.extract_item(0)

            # Select which output library to send this spectrum to
            output_index = 0

            # Contaminate this spectrum is requested


            # Process spectra through 4FS
            degraded_spectra = etc_wrapper.process_spectra(
                spectra_list=((input_spectrum, input_spectrum_continuum_normalised),)
            )

            # Import spectra into output spectrum library
            output_libraries[output_index].insert(spectra=input_spectrum,
                                                  filenames=input_spectrum['filename'])

            output_libraries[output_index].insert(spectra=input_spectrum_continuum_normalised,
                                                  filenames=continuum_normalised_spectrum_id[0]['filename'])
