#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take the APOKASC training set and test sets, apply random radial velocities to the spectra, and see how well fourgp_rv
can determine what radial velocity we applied.
"""

from os import path as os_path
import argparse
import logging
import time
import random
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite, SpectrumPolynomial
from fourgp_rv import RvInstance

# Set up logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info("Testing fourgp_rv")

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--vary_mcmc_steps', action='store_true')
parser.add_argument('--output_file', default="./test_cannon.out", dest='output_file')
args = parser.parse_args()

# Set path to workspace where we expect to find a library of template spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "workspace")
target_library_name = "brani_rv_grid"
library_path = os_path.join(workspace, target_library_name)

# Instantiate the RV code
time_start = time.time()
rv_code = RvInstance.from_spectrum_library_sqlite(library_path=library_path)
n_burn_default= rv_code.n_burn
n_steps_default = rv_code.n_steps
time_end = time.time()
logger.info("Set up time was {:.2f} sec".format(time_end - time_start))

# Open the library of APOKASC test spectra
test_library_name = "testset_HRS"
test_library_path = os_path.join(workspace, test_library_name)
test_library = SpectrumLibrarySqlite(path=test_library_path, create=False)

# Load test set
test_library_ids = [i["specId"] for i in test_library.search()]

# Pick some random spectra
indices = [random.randint(0, len(test_library_ids) - 1) for i in range(400)]

# Start writing output
with open(args.output_file, "w") as output:

    # Loop over the spectra we are going to test
    for index in indices:
        # Look up database ID of the test spectrum
        test_id = test_library_ids[index]

        # Load test spectrum
        test_spectrum = test_library.open(ids=[test_id]).extract_item(0)

        # Pick a random number of MCMC steps to do
        if args.vary_mcmc_steps:
            rv_code.n_burn = rv_code.n_steps = random.randint(200, 1500)

        # Pick a random radial velocity
        radial_velocity = random.uniform(-200, 200)  # Unit km/s

        # Pick coefficients for some random continuum
        continuum = (random.uniform(1, 100), random.uniform(-1e-2, 1e-2), random.uniform(-1e-8, 1e-8))
        continuum_spectrum = SpectrumPolynomial(wavelengths=test_spectrum.wavelengths, terms=2, coefficients=continuum)

        test_spectrum_with_continuum = test_spectrum * continuum_spectrum
        test_spectrum_with_rv = test_spectrum_with_continuum.apply_radial_velocity(radial_velocity*1000)  # Unit m/s

        time_start = time.time()
        stellar_labels = rv_code.fit_rv(test_spectrum_with_rv)
        time_end = time.time()

        output.write("{:5d} {:9.1f} {:11.3f} {:11.3f}\n".format(rv_code.n_steps, time_end-time_start, radial_velocity, stellar_labels["velocity"]))
        output.flush()

