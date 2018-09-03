#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python rearrange.py>, but <./rearrange.py> will not work.

"""
Take a library (or libraries) of spectra, and rearrange the spectra within them. For example, we can merge multiple
input libraries into one output library, or split one input library randomly between multiple outputs. We can slice
an input library based on some metadata constraints, and store only a subset of the input spectra.

We can also contaminate the input spectra with some fraction of light from a contaminating spectrum.
"""

import argparse
import os
from os import path as os_path
import time
import random
import logging

from fourgp_speclib import SpectrumLibrarySqlite
import fourgp_degrade

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-library',
                    action="append",
                    dest="input_library",
                    help="The name of the spectrum library(s) we are to read input spectra from. A subset of the stars "
                         "in the input library may optionally be selected by suffixing its name with a comma-separated "
                         "list of constraints in [] brackets. Use the syntax my_library[Teff=3000] to demand equality, "
                         "or [0<[Fe/H]<0.2] to specify a range. We do not currently support other operators like "
                         "[Teff>5000], but such ranges are easy to recast is a range, e.g. [5000<Teff<9999]. "
                         "Multiple inputs can be specified on one command line to merge libraries.")
parser.add_argument('--output-library',
                    action="append",
                    dest="output_library",
                    help="The name of the spectrum library we are to feed output into. Multiple output destinations "
                         "can be specified on one command line, in which case the --output-fraction setting should "
                         "be used to randomly direct spectra into the various destinations with specified "
                         "probabilities.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find (and create) spectrum libraries.")
parser.add_argument('--contamination-library',
                    action="append",
                    dest="contamination_library",
                    help="Contaminate output spectra with a randomly chosen spectrum from this library. A subset of "
                         "the stars in the input library may optionally be selected by suffixing its name with a "
                         "comma-separated  list of constraints in [] brackets. Use the syntax my_library[Teff=3000] "
                         "to demand equality, or [0<[Fe/H]<0.2] to specify a range. We do not currently support "
                         "other operators like [Teff>5000], but such ranges are easy to recast is a range, e.g. "
                         "[5000<Teff<9999]. Multiple contamination libraries can be specified, in which case a "
                         "contaminating source is picked at random from one of the libraries.")
parser.add_argument('--contamination-fraction',
                    action="append",
                    dest="contamination_fraction",
                    help="The fraction of photons which should come from contaminating sources. Multiple values can "
                         "be specified on one command line, in which case each input spectrum turns into multiple "
                         "output spectra, contaminated with each contamination fraction in turn. Default is zero.")
parser.add_argument('--output-fraction',
                    action="append",
                    dest="output_fraction",
                    help="If multiple output libraries are specified, the input spectra are randomly split between "
                         "them. Specify the fraction to end up in each output library.")
parser.add_argument('--create',
                    action='store_true',
                    dest="create",
                    help="Create a clean spectrum library to feed output spectra into. Will throw an error if "
                         "a spectrum library already exists with the same name.")
parser.add_argument('--no-create',
                    action='store_false',
                    dest="create",
                    help="Do not create a clean spectrum library to feed output spectra into.")
parser.set_defaults(create=True)
parser.add_argument('--log-file',
                    required=False,
                    default="/tmp/rearrange_{}.log".format(pid),
                    dest="log_to",
                    help="Specify a log file where we log our progress.")
args = parser.parse_args()

logger.info("Running rearrange on spectra from <{}>, going into <{}>, contaminating with <{}>".
            format(args.input_library, args.output_library, args.contamination_library))

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")
os.system("mkdir -p {}".format(workspace))


def make_weighted_choice(weights):
    """
    Utility function to make weighted random choices. Pass a list of floats representing the weights of a series of
    options. Get back the index of the option that was selected.

    :param weights:
    list of floats, representing the weights of the options
    :return:
    int. index selected.
    """
    weights_sum = sum(weights)
    selected_index = 0
    output_select = random.uniform(a=0, b=weights_sum)
    for index, weight in enumerate(weights):
        output_select -= weight
        if output_select <= 0:
            selected_index = index
            break
    return selected_index


# Open input spectrum library(s), and fetch a list of all the flux-normalised spectra within each
input_libraries = []

if args.input_library is not None:
    input_libraries = [SpectrumLibrarySqlite.open_and_search(library_spec=item,
                                                             workspace=workspace,
                                                             extra_constraints={"continuum_normalised": 0}
                                                             )
                       for item in args.input_library]

# Report to user how many spectra we have just found
logger.info("Opening {:d} input libraries. These contain {:s} spectra.".
            format(len(input_libraries), [len(x['items']) for x in input_libraries]))

# Open contaminating spectrum library(s), if any, and fetch a list of all the flux-normalised spectra within each
contamination_libraries = []
if args.contamination_library is not None:
    contamination_libraries = [SpectrumLibrarySqlite.open_and_search(library_spec=item,
                                                                     workspace=workspace,
                                                                     extra_constraints={"continuum_normalised": 0}
                                                                     )
                               for item in args.contamination_library]

contamination_spectra = []
for library in contamination_libraries:
    library_obj = library["library"]
    for item in library["items"]:
        contamination_spectrum = library_obj.open(ids=item['specId']).extract_item(0)

        # Look up the name of the star we've just loaded
        object_uid = contamination_spectrum.metadata['Starname']

        # Search for the continuum-normalised version of this same object
        search_constraints = {
            "Starname": object_uid,
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

logger.info("We have {:d} contamination spectra.".format(len(contamination_spectra)))

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

# Process each spectrum in turn
with open(args.log_to, "w") as result_log:
    # Loop over all the contamination fractions we're applying
    for contamination_fraction in contamination_fractions:
        # Loop over spectra to process
        for input_library in input_libraries:
            library_obj = input_library["library"]
            for input_spectrum_id in input_library["items"]:
                logger.info("Working on <{}>".format(input_spectrum_id['filename']))

                # Open input spectrum data from disk
                input_spectrum_array = library_obj.open(ids=input_spectrum_id['specId'])
                input_spectrum = input_spectrum_array.extract_item(0)

                # Look up the name of the star we've just loaded
                spectrum_matching_field = 'uid' if 'uid' in input_spectrum.metadata else 'Starname'
                object_uid = input_spectrum.metadata[spectrum_matching_field]
                object_name = input_spectrum.metadata['Starname']

                # Write log message
                result_log.write("\n[{}] {}".format(time.asctime(), object_uid))
                result_log.flush()

                # Search for the continuum-normalised version of this same object
                search_constraints = {
                    spectrum_matching_field: object_uid,
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
                    # Pick a random spectrum to contaminate with
                    contamination_spectrum, contamination_spectrum_continuum_normalised = \
                        random.choice(contamination_spectra)

                    # Work out the integrated flux in the input and contaminating spectra
                    input_integral = input_spectrum.integral()
                    contamination_integral = contamination_spectrum.integral()

                    # Interpolate the contamination spectrum onto the observed spectrum's wavelength
                    resampler = fourgp_degrade.SpectrumResampler(contamination_spectrum)
                    contamination_resampled = resampler.match_to_other_spectrum(other=input_spectrum,
                                                                                resample_errors=False,
                                                                                resample_mask=False)

                    resampler = fourgp_degrade.SpectrumResampler(contamination_spectrum_continuum_normalised)
                    contamination_cn_resampled = resampler.match_to_other_spectrum(other=input_spectrum,
                                                                                   resample_errors=False,
                                                                                   resample_mask=False)

                    # Renormalise contaminating spectrum to same integrated flux as input spectrum
                    contamination_resampled.values *= input_integral / contamination_integral

                    # Flux components from input spectrum, and from contamination source
                    flux_from_input = input_spectrum.values * (1 - contamination_fraction)
                    flux_from_contamination = contamination_resampled.values * contamination_fraction

                    # Fraction of flux in each pixel coming from input spectrum versus contaminating spectrum
                    pixel_weights = flux_from_input / (flux_from_input + flux_from_contamination)

                    # Pollute flux normalised spectrum
                    input_spectrum.values = flux_from_input + flux_from_contamination

                    # Pollute continuum normalised spectrum
                    input_spectrum_continuum_normalised.values = \
                        (input_spectrum_continuum_normalised.values * pixel_weights +
                         contamination_cn_resampled.values * (1-pixel_weights))

                    # Add metadata describing pollution fraction
                    input_spectrum_continuum_normalised.metadata["contamination_fraction"] = \
                    input_spectrum.metadata["contamination_fraction"] = contamination_fraction

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
