#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python rv_test.py>, but <./rv_test.py> will not work.

"""
Take the GALAH test sample of spectra, apply random radial velocities to the spectra, and see how well Sergey Koposov's
RV code can determine what radial velocity we applied.
"""

import argparse
import logging
import random
import time
import json
from os import path as os_path

from fourgp_fourfs import FourFS
from fourgp_rv import random_radial_velocity
from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../../../..")
parser = argparse.ArgumentParser(description=__doc__.strip())
parser.add_argument('--test-library',
                    required=False,
                    default='galah_test_sample_turbospec',
                    dest='test_library',
                    help="Library of spectra to test the RV code on")
parser.add_argument('--snr',
                    required=False,
                    default='50',
                    dest='snr',
                    help="The SNR/pixel at which we are to simulate observations of test spectra using 4FS")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--templates-directory',
                    required=False,
                    default="/mnt/data/phoenix/4most_templates",
                    dest="templates_directory",
                    help="The path where we find the resampled template spectra, together with an SQLite3 "
                         "database listing the templates we have.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where 4FS binary package is installed.")
parser.add_argument('--output-file',
                    default="./test_rv_code.out",
                    dest='output_file',
                    help="Data file to write output to")
parser.add_argument('--test-count',
                    required=False,
                    default=400,
                    type=int,
                    dest="test_count",
                    help="Run n tests.")
args = parser.parse_args()

# Set up logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info("Testing Sergey's RV code")

# Set path to workspace where we expect to find libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

# Open test set
spectra = SpectrumLibrarySqlite.open_and_search(
    library_spec=args.test_library,
    workspace=workspace,
    extra_constraints={"continuum_normalised": 0}
)
test_library, test_library_items, test_spectra_constraints = [spectra[i] for i in ("library", "items","constraints")]

# Instantiate 4FS wrapper
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
    snr_list=[float(args.snr)],
    snr_per_pixel=True
)

# Read information about the wavelength rasters we need to resample the test spectra onto
rv_code_wavelength_arms = json.loads(open(os_path.join(args.templates_directory, "arm_list.json"), "rt").read())

# Pick some random spectra
indices = [random.randint(0, len(test_library_items) - 1) for i in range(args.test_count)]

# Start writing output
with open(args.output_file, "w") as output:
    column_headings_written = False
    stellar_label_names = []

    # Loop over the spectra we are going to test
    for index in indices:
        # Look up database ID of the test spectrum
        test_id = test_library_items[index]['id']

        # Load test spectrum (flux normalised)
        test_spectrum = test_library.open(ids=[test_id]).extract_item(0)

        # Look up the unique ID of the star we've just loaded
        # Newer spectrum libraries have a uid field which is guaranteed unique; for older spectrum libraries use
        # Starname instead.

        # Work out which field we're using (uid or Starname)
        spectrum_matching_field = 'uid' if 'uid' in test_spectrum.metadata else 'Starname'

        # Look up the unique ID of this object
        object_name = test_spectrum.metadata[spectrum_matching_field]

        # Search for the continuum-normalised version of this same object (which will share the same uid / name)
        search_criteria = test_spectra_constraints.copy()
        search_criteria[spectrum_matching_field] = object_name
        search_criteria['continuum_normalised'] = 1
        continuum_normalised_spectrum_id = test_library.search(**search_criteria)

        # Check that continuum-normalised spectrum exists and is unique
        assert len(continuum_normalised_spectrum_id) == 1, "Could not find continuum-normalised spectrum."

        # Load the continuum-normalised version
        test_spectrum_continuum_normalised_arr = test_library.open(
            ids=continuum_normalised_spectrum_id[0]['specId']
        )

        # Turn the SpectrumArray we got back into a single Spectrum
        test_spectrum_continuum_normalised = test_spectrum_continuum_normalised_arr.extract_item(0)

        # Pick a random radial velocity
        radial_velocity = random_radial_velocity()  # Unit km/s

        # Apply radial velocity to both flux- and continuum-normalised spectra (method expects velocity in m/s)
        test_spectrum_with_rv = test_spectrum.apply_radial_velocity(
            v=radial_velocity * 1000
        )

        test_spectrum_continuum_normalised_with_rv = test_spectrum_continuum_normalised.apply_radial_velocity(
            v=radial_velocity * 1000
                                                                                                              )

        # Now create a mock observation of this spectrum using 4FS
        mock_observed_spectra = etc_wrapper.process_spectra(
            spectra_list=((test_spectrum, test_spectrum_continuum_normalised),)
        )

        # Loop over LRS and HRS
        for mode in mock_observed_spectra:
            # Loop over the spectra we simulated (there was only one!)
            for index in mock_observed_spectra[mode]:
                # Extract continuum-normalised mock observation
                observed = mock_observed_spectra[mode][index][float(args.snr)]['spectrum_continuum_normalised']

                # Run RV code and calculate how much CPU time we used
                time_start = time.time()
                stellar_labels = rv_code.fit_rv(test_spectrum_with_rv)
                time_end = time.time()

                # If this is the first object, write column headers
                if not column_headings_written:
                    line1 = "# {:5s} {:7s} {:11s} ".format("Steps", "Time", "RV_in")
                    line2 = "# {:5d} {:7d} {:11d} ".format(1, 2, 3)
                    column_counter = 3
                    stellar_label_names = list(stellar_labels.keys())
                    stellar_label_names.sort()
                    for key in stellar_label_names:
                        column_counter += 1
                        line2 = "%-*s %s" % (len(line1), line2, column_counter)
                        line1 += "{}_out ".format(key)
                    for key in test_library.list_metadata_fields():
                        column_counter += 1
                        line2 = "%-*s %s" % (len(line1), line2, column_counter)
                        line1 += "{} ".format(key)
                    output.write("{}\n{}\n".format(line1, line2))
                    column_headings_written = True

                # Write a line to the output data file
                line = "{:5d} {:9.1f} {:11.3f} ".format(rv_code.n_steps, time_end - time_start, radial_velocity)
                for key in stellar_label_names:
                    line += "{} ".format(stellar_labels.get(key, "-"))
                for key in test_library.list_metadata_fields():
                    line += "{} ".format(test_spectrum.metadata.get(key, "-"))

                output.write(line + "\n")
                output.flush()
