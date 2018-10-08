#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python internal_model_span_wavelength.py>, but <./internal_model_span_wavelength.py> will not work.

"""
Take an output file from the Cannon, and create a spectrum library containing the Cannon's predictive model of how the
spectrum of each test object should look.
"""

import argparse
import gzip
import json
import os
import re
import logging
from os import path as os_path

import numpy as np
from fourgp_cannon import CannonInstance_2018_01_09
from fourgp_speclib import SpectrumLibrarySqlite, Spectrum


def dict_merge(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


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


# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cannon-output',
                    required=True,
                    dest='cannon',
                    help="Filename of the JSON file containing the label values estimated by the Cannon, without "
                         "the <.summary.json.gz> suffix.")
parser.add_argument('--output-library',
                    required=False,
                    default="cannon_internal_model",
                    dest="output_library",
                    help="The name of the spectrum library we are to feed the Cannon's predictive model into.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
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
args = parser.parse_args()

# Set path to workspace where we create libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../../workspace")
os.system("mkdir -p {}".format(workspace))

# Fetch metadata about this Cannon run
cannon_output = json.loads(gzip.open(args.cannon + ".full.json.gz", "rt").read())
description = cannon_output['description']

# Open spectrum library we originally trained the Cannon on
training_spectra_info = SpectrumLibrarySqlite.open_and_search(
    library_spec=cannon_output["train_library"],
    workspace=workspace,
    extra_constraints={"continuum_normalised": 1}
)

training_library, training_library_items = [training_spectra_info[i] for i in ("library", "items")]

# Load training set
training_library_ids_all = [i["specId"] for i in training_library_items]
training_spectra_all = training_library.open(ids=training_library_ids_all)

# If requested, fill in any missing labels on the training set by assuming scaled-solar abundances
if cannon_output['assume_scaled_solar']:
    training_spectra = autocomplete_scaled_solar_abundances(
        input_spectra=training_spectra_all,
        label_list=cannon_output["labels"]
    )
else:
    training_spectra = filter_training_spectra(
        input_spectra=training_spectra_all,
        label_list=cannon_output["labels"],
        input_library=training_library,
        input_spectrum_ids=training_library_ids_all
    )

# Recreate the mask that was used when the Cannon was trained
censoring_masks = cannon_output["censoring_mask"]
if censoring_masks is not None:

    # Overall mask is a map of all the pixels we use in this Cannon fit
    overall_mask = np.zeros_like(cannon_output['wavelength_raster'], dtype=np.bool)

    # Items in the censoring_mask dictionary are True for every pixel that is *excluded*
    for key, value in censoring_masks.items():
        censoring_masks[key] = np.asarray(value, dtype=np.bool)

        # Invert the censor mask to get a list of the pixels we actually use
        overall_mask += ~censoring_masks[key]

        logger.info("Mask for label <{}> includes {:d} pixels.".format(key, sum(~censoring_masks[key])))
else:
    # No mask; use all pixels
    overall_mask = np.ones_like(cannon_output['wavelength_raster'], dtype=np.bool)

# Display mask information
logger.info("Mask includes {:d} of {:d} pixels.".format(sum(overall_mask),
                                                        len(cannon_output['wavelength_raster']))
            )

# Recreate a Cannon instance, using the saved state
model = CannonInstance_2018_01_09(training_set=training_spectra,
                                  load_from_file=args.cannon + ".cannon",
                                  label_names=cannon_output["labels"],
                                  censors=censoring_masks,
                                  threads=None
                                  )
cannon = model._model

# Create new spectrum library for output
library_name = re.sub("/", "_", args.output_library)
library_path = os_path.join(workspace, library_name)
output_library = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Query Cannon's internal model of each test spectrum in turn
for test_item in cannon_output['spectra']:
    label_values = test_item['cannon_output'].copy()
    label_vector = np.asarray([label_values[key] for key in cannon_output["labels"]])
    cannon_predicted_spectrum = cannon.predict(label_vector)[0]

    spectrum_object = Spectrum(wavelengths=cannon.dispersion[overall_mask],
                               values=cannon_predicted_spectrum[overall_mask],
                               value_errors=cannon.s2[overall_mask]
                               )

    output_library.insert(spectra=spectrum_object,
                          filenames=test_item['Starname'],
                          metadata_list=dict_merge(test_item['spectrum_metadata'], test_item['cannon_output'])
                          )
