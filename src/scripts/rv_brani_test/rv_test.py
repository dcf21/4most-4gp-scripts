#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python rv_test.py>, but <./rv_test.py> will not work.

"""
Take the APOKASC training set and test sets, apply random radial velocities to the spectra, and see how well fourgp_rv
can determine what radial velocity we applied.
"""

from os import path as os_path
import argparse
import logging
import time
import random

from fourgp_speclib import SpectrumLibrarySqlite, SpectrumPolynomial
from fourgp_rv import RvInstance, random_radial_velocity

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--template-library',
                    required=False,
                    default='brani_rv_grid',
                    dest='template_library',
                    help="Library of template spectra we match spectra against.")
parser.add_argument('--test-library',
                    required=False,
                    default='hawkins_apokasc_test_set_hrs',
                    dest='test_library',
                    help="Library of spectra to test the RV code on.")
parser.add_argument('--vary-mcmc-steps',
                    action='store_true',
                    dest="vary_mcmc_steps",
                    help="If set, we vary the number of MCMC steps used to try to match the RV, "
                         "making it possible to gauge how many steps are needed to get good results.")
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

logger.info("Testing fourgp_rv")

# Set path to workspace where we expect to find a library of template spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "../../../workspace")
target_library_name = args.template_library
library_path = os_path.join(workspace, target_library_name)

# Instantiate the RV code
time_start = time.time()
rv_code = RvInstance.from_spectrum_library_sqlite(library_path=library_path)
n_burn_default = rv_code.n_burn
n_steps_default = rv_code.n_steps
time_end = time.time()
logger.info("Set up time was {:.2f} sec".format(time_end - time_start))

# Open the library of APOKASC test spectra
test_library_name = args.test_library
test_library_path = os_path.join(workspace, test_library_name)
test_library = SpectrumLibrarySqlite(path=test_library_path, create=False)

# Load test set
test_library_ids = [i["specId"] for i in test_library.search()]

# Pick some random spectra
indices = [random.randint(0, len(test_library_ids) - 1) for i in range(args.test_count)]

# Start writing output
with open(args.output_file, "w") as output:
    column_headings_written = False
    stellar_label_names = []

    # Loop over the spectra we are going to test
    for index in indices:
        # Look up database ID of the test spectrum
        test_id = test_library_ids[index]

        # Load test spectrum
        test_spectrum = test_library.open(ids=[test_id]).extract_item(0)

        # Pick a number of MCMC steps to do
        if args.vary_mcmc_steps:
            rv_code.n_burn = rv_code.n_steps = random.randint(100, 1000)
        else:
            rv_code.n_burn = rv_code.n_steps = 500

        # Pick a random radial velocity
        radial_velocity = random_radial_velocity()  # Unit km/s

        # Pick coefficients for some random continuum
        continuum = (random.uniform(1, 100), random.uniform(-1e-2, 1e-2), random.uniform(-1e-8, 1e-8))
        continuum_spectrum = SpectrumPolynomial(wavelengths=test_spectrum.wavelengths, terms=2, coefficients=continuum)

        test_spectrum_with_continuum = test_spectrum * continuum_spectrum
        test_spectrum_with_rv = test_spectrum_with_continuum.apply_radial_velocity(radial_velocity * 1000)  # Unit m/s

        # Run RV code and calculate how much CPU time we used
        time_start = time.time()
        stellar_labels = rv_code.fit_rv(test_spectrum_with_rv)
        time_end = time.time()

        # If this is the first object, write column headers
        if not column_headings_written:
            line1 = "# {:5s} {:7s} {:11s} ".format("Steps", "Time", "RV_in")
            line2 = "# {:5d} {:7d} {:11d} ".format(1, 2, 3)
            column_counter = 3
            stellar_label_names = stellar_labels.keys()
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
