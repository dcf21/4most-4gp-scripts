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
import numpy as np
import scipy.constants

from fourgp_fourfs import FourFS
from fourgp_degrade.resample import SpectrumResampler
from fourgp_rv import random_radial_velocity
from fourgp_speclib import SpectrumLibrarySqlite

from rvspecfit import spec_fit, fitter_ccf, vel_fit, frozendict

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
                    default="/mnt/data/phoenix/4most_templates/",
                    dest="templates_directory",
                    help="The path where we find the resampled template spectra, together with an SQLite3 "
                         "database listing the templates we have.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where 4FS binary package is installed.")
parser.add_argument('--output-file',
                    default="./test_rv_code",
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
test_library, test_library_items, test_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

# Instantiate 4FS wrapper
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
    snr_list=[float(args.snr)],
    snr_per_pixel=True
)

# Read information about the wavelength rasters we need to resample the test spectra onto
rv_code_wavelength_arms = json.loads(open(os_path.join(args.templates_directory, "arm_list.json"), "rt").read())

# Construct the raster for each wavelength arm
arm_rasters = {}

for arm_name, raster_spec in rv_code_wavelength_arms.items():
    mode, sub_arm = arm_name.split("_")

    if mode not in arm_rasters:
        arm_rasters[mode] = []

    # This must EXACTLY match the wavelength raster generated in <rvspecfit/py/rvspecfit/make_interpol.py:125>
    deltav = 1000.  # extra padding
    fac1 = (1 + deltav / (scipy.constants.speed_of_light / 1e3))

    arm_rasters[mode].append({'name': arm_name,
                              'raster': np.exp(
                                  np.arange(
                                      np.log(raster_spec['lambda_min'] / fac1),
                                      np.log(raster_spec['lambda_max'] * fac1),
                                      np.log(1 + raster_spec['lambda_step'] / raster_spec['lambda_min'])))
                              })

# Pick some random spectra
indices = [random.randint(0, len(test_library_items) - 1) for i in range(args.test_count)]

# Start writing output
output_files = {}
format_str = "{:5} {:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10}"

for mode in arm_rasters.keys():
    output_files[mode] = open("{}_{}.dat".format(args.output_file, mode), "wt")

    # Write column headers
    output_files[mode].write("# {}\n".format(format_str).format("Time",
                                                                "RV_in", "RV_out", "RV_err",
                                                                "Teff_in", "Teff_out", "Teff_err",
                                                                "logg_in", "logg_out", "logg_err",
                                                                "feh_in", "feh_out", "feh_err")
                             )
    output_files[mode].write("# {}\n".format(format_str).format(*range(13)))

# Loop over the spectra we are going to test
for counter, index in enumerate(indices):
    # Look up database ID of the test spectrum
    test_id = test_library_items[index]['specId']

    # Load test spectrum (flux normalised)
    test_spectrum = test_library.open(ids=[test_id]).extract_item(0)

    # Look up the unique ID of the star we've just loaded
    # Newer spectrum libraries have a uid field which is guaranteed unique; for older spectrum libraries use
    # Starname instead.

    # Work out which field we're using (uid or Starname)
    spectrum_matching_field = 'uid' if 'uid' in test_spectrum.metadata else 'Starname'

    # Look up the unique ID of this object
    object_name = test_spectrum.metadata[spectrum_matching_field]
    logger.info("Working on test {:6d} (spectrum <{}>)".format(counter, object_name))
    logger.info("Spectrum metadata: {}".format(str(test_spectrum.metadata)))

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
    logger.info("Applying radial velocity {:6.1f} km/s to spectrum".format(radial_velocity))

    # Apply radial velocity to both flux- and continuum-normalised spectra (method expects velocity in m/s)
    test_spectrum_with_rv = test_spectrum.apply_radial_velocity(
        v=radial_velocity * 1000
    )

    test_spectrum_continuum_normalised_with_rv = test_spectrum_continuum_normalised.apply_radial_velocity(
        v=radial_velocity * 1000
    )

    # Now create a mock observation of this spectrum using 4FS
    logger.info("Passing spectrum through 4FS")
    mock_observed_spectra = etc_wrapper.process_spectra(
        spectra_list=((test_spectrum, test_spectrum_continuum_normalised),)
    )

    # Loop over LRS and HRS
    for mode in mock_observed_spectra:
        mode_lower = mode.lower()

        # Loop over the spectra we simulated (there was only one!)
        for index in mock_observed_spectra[mode]:
            time_start = time.time()

            # Extract continuum-normalised mock observation
            logger.info("Resampling {} spectrum".format(mode))
            observed = mock_observed_spectra[mode][index][float(args.snr)]['spectrum_continuum_normalised']
            resampler = SpectrumResampler(observed)

            # Loop over each arm of this 4MOST mode in turn, populating a list of the observed spectra
            spectral_data = []
            for arm in arm_rasters[mode_lower]:
                observed_arm = resampler.onto_raster(arm['raster'])
                spectral_data.append(
                    spec_fit.SpecData(name=arm['name'],
                                      lam=arm['raster'],
                                      spec=observed_arm.values,
                                      espec=observed_arm.value_errors,
                                      badmask=None
                                      )
                )

            # Run RV code
            config = frozendict.frozendict({
                'template_lib': args.templates_directory
            })

            options = {
                'npoly': 15
            }

            # 1. fitter_ccf
            logger.info("Calling <fitter_ccf.fit> on {} spectrum".format(mode))
            res = fitter_ccf.fit(specdata=spectral_data, config=config)
            logger.info("Initial guess velocity: {}".format(str(res['best_vel'])))
            logger.info("Initial guess parameters: {}".format(str(res['best_par'])))
            t2 = time.time()

            # 2. vel_fit
            logger.info("Calling <vel_fit.process> on {} spectrum".format(mode))
            paramDict0 = res['best_par']
            fixParam = []
            if res['best_vsini'] is not None:
                paramDict0['vsini'] = res['best_vsini']
            res1 = vel_fit.process(
                specdata=spectral_data,
                paramDict0=paramDict0,
                fixParam=fixParam,
                config=config,
                options=options)
            t3 = time.time()

            # 3. get_chisq_continuum
            logger.info("Calling <spec_fit.get_chisq_continuum> on {} spectrum".format(mode))
            chisq_cont_array = spec_fit.get_chisq_continuum(specdata=spectral_data, options=options)
            t4 = time.time()

            # Calculate how much CPU time we used
            time_end = time.time()

            # Write a line to the output data file
            output_files[mode_lower].write("  {}\n".format(format_str).format(
                time_end - time_start,
                radial_velocity, res1.get('vel', '-'), res1.get('vel_err', '-'),
                test_spectrum.metadata.get('Teff', '-'),
                res1['param'].get('teff', '-'),
                res1['param_err'].get('teff', '-'),
                test_spectrum.metadata.get('logg', '-'),
                res1['param'].get('logg', '-'),
                res1['param_err'].get('logg', '-'),
                test_spectrum.metadata.get('[Fe/H]', '-'),
                res1['param'].get('feh', '-'),
                res1['param_err'].get('feh', '-'),
            ))

            # Make sure that output data file is always kept up to date
            output_files[mode_lower].flush()
