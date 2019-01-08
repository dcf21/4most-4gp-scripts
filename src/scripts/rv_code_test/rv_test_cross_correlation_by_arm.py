#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python rv_test_cross_correlation.py>, but <./rv_test_cross_correlation.py> will not work.

"""
Take the GALAH test sample of spectra, apply random radial velocities to the spectra, and see how well a simple
cross-correlation RV code can determine what radial velocity we applied.

We work out the RV from each arm separately, and create separate data files for each arm.
"""

import argparse
import logging
import os
import random
import sys
import time
from collections import namedtuple
from os import path as os_path

import numpy as np
from fourgp_fourfs import FourFS
from fourgp_rv import random_radial_velocity, RvInstanceCrossCorrelation
from fourgp_rv.templates_resample import resample_templates
from fourgp_speclib import SpectrumLibrarySqlite

# Create unique ID for this process
run_id = os.getpid()


# Helper function to measure CPU time
def get_cpu_time(pid):
    stats = open("/proc/{:d}/stat".format(pid)).read().split()
    u_time = float(stats[13])
    s_time = float(stats[14])
    return u_time + s_time


# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../../../..")
parser = argparse.ArgumentParser(description=__doc__.strip())
parser.add_argument('--test-library',
                    required=False,
                    default='rv_test_objects',
                    dest='test_library',
                    help="Library of spectra to test the RV code on")
parser.add_argument('--snr',
                    required=False,
                    default='50',
                    dest='snr',
                    help="The SNR/pixel at which we are to simulate observations of test spectra using 4FS")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--templates-library',
                    required=False,
                    default="rv_templates_resampled",
                    dest="templates_library",
                    help="The path where we find the template spectra we are going to use in the fitting.")
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
                    default=20000,
                    type=int,
                    dest="test_count",
                    help="Run n tests.")

parser.add_argument('--interpolation', default="quadratic", dest='interpolation',
                    choices=("quadratic", "spline"),
                    help="Select what functional form to use when doing sub-pixel interpolation of the CCF")
parser.add_argument('--interpolation-pixels', default=3, dest='interpolation_pixels',
                    type=int,
                    help="Select the number of pixels to use when doing sub-pixel interpolation of the CCF")
parser.add_argument('--upsampling', default=1, dest='upsampling',
                    type=int,
                    help='Upsample both the template spectra and the test spectra before doing cross-correlation')

parser.add_argument('--correlate-with-test-spectrum',
                    action='store_true',
                    dest="correlate_with_test_spectrum",
                    help="Specify that we cross-correlate with the test spectrum itself, at zero RV, as a sanity "
                         "check.")
parser.add_argument('--correlate-with-templates',
                    action='store_false',
                    dest="correlate_with_test_spectrum",
                    help="Specify that we cross-correlate with a library of template spectra (default).")
parser.set_defaults(correlate_with_test_spectrum=False)

parser.add_argument('--zero-rv',
                    action='store_true',
                    dest="zero_rv",
                    help="Specify that we do not inject any RVs into the test spectra; their true RVs are zero.")
parser.add_argument('--non-zero-rv',
                    action='store_false',
                    dest="zero_rv",
                    help="Specify that we inject non-zero RVs into the test spectra (default).")
parser.set_defaults(zero_rv=False)
args = parser.parse_args()

# Set up logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info("Testing Cross-Correlation RV code")

# Set path to workspace where we expect to find libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

# Open test set
spectra = SpectrumLibrarySqlite.open_and_search(
    library_spec=args.test_library,
    workspace=workspace,
    extra_constraints={"continuum_normalised": 0}
)
test_library, test_library_items, test_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

# Open template spectrum library
template_library = SpectrumLibrarySqlite(
    path=os_path.join(workspace, args.templates_library),
    create=False,
)

# Instantiate RV code
rv_calculator = RvInstanceCrossCorrelation(
    spectrum_library=template_library,
    upsampling=args.upsampling
)

# Instantiate 4FS wrapper
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
    magnitude=13,
    snr_list=[float(args.snr)],
    snr_per_pixel=True,
    identifier="rv_test"
)

# Pick some random spectra
indices = [random.randint(0, len(test_library_items) - 1) for i in range(args.test_count)]

# Start writing output
output_files = {}
format_str = "{:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10} {:10}"

for mode in ("HRS", "LRS"):
    for arm_name in rv_calculator.templates_by_arm[mode].keys():
        output_files[arm_name] = open("{}_{}_{}.dat".format(args.output_file, arm_name, run_id), "wt")

        # Write column headers
        output_files[arm_name].write("# {}\n".format(" ".join(sys.argv[:])))
        output_files[arm_name].write("# SNR/pixel = {}\n".format(args.snr))
        output_files[arm_name].write("# Pixel multiplicative spacing = {:.16f}\n".format(
            rv_calculator.arm_properties[arm_name]['multiplicative_step']
        ))

        output_files[arm_name].write("# {}\n".format(format_str).format("Time",
                                                                        "Teff_in", "Teff_out",
                                                                        "log(g)_in", "log(g)_out",
                                                                        "[Fe/H]_in", "[Fe/H]_out",
                                                                        "RV_in", "RV_out", "RV_err")
                                     )
        output_files[arm_name].write("# {}\n".format(format_str).format(*range(10)))

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
    # logger.info("Spectrum metadata: {}".format(str(test_spectrum.metadata)))

    # If we're cross-correlating with the test spectrum itself, create an RV code instance to do that now
    if args.correlate_with_test_spectrum:
        tmp_template_library = "tmp_{}".format(run_id)

        os.system("rm -Rf {}".format(os_path.join(workspace, tmp_template_library)))

        # Create template spectrum library
        resample_templates(logger=logger,
                           args=namedtuple("arguments", ("templates_in", "workspace", "templates_out", "binary_path"))
                           ("{}[{}={}]".format(args.test_library, spectrum_matching_field, object_name),
                            workspace, tmp_template_library, root_path)
                           )

        # Open template spectrum library
        template_library = SpectrumLibrarySqlite(
            path=os_path.join(workspace, tmp_template_library),
            create=False,
        )

        # Instantiate RV code
        rv_calculator = RvInstanceCrossCorrelation(
            spectrum_library=template_library,
            upsampling=args.upsampling
        )

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
    if not args.zero_rv:
        radial_velocity = random_radial_velocity()  # Unit km/s
    else:
        radial_velocity = 0.

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
        spectra_list=((test_spectrum_with_rv, test_spectrum_continuum_normalised_with_rv),)
    )

    # Loop over LRS and HRS
    for mode in mock_observed_spectra:
        # Loop over the spectra we simulated (there was only one!)
        for fourfs_index in mock_observed_spectra[mode]:

            # Extract continuum-normalised mock observation
            logger.info("Resampling {} spectrum".format(mode))
            observed = mock_observed_spectra[mode][fourfs_index][float(args.snr)]['spectrum_continuum_normalised']

            # Replace errors which are nans with a large value, otherwise they cause numerical failures in the RV code
            observed.value_errors[np.isnan(observed.value_errors)] = 1000.

            # Check for NaNs in actual spectrum
            if not np.all(np.isfinite(observed.values)):
                print("Warning: NaN values in test spectrum!")
                observed.value_errors[np.isnan(observed.values)] = 1000.
                observed.values[np.isnan(observed.values)] = 1.

            for arm_name in rv_calculator.templates_by_arm[mode].keys():
                time_start = time.time()
                time_start_cpu = get_cpu_time(run_id)

                rv_mean, rv_std_dev, stellar_parameters, rv_estimates = \
                    rv_calculator.estimate_rv(input_spectrum=observed,
                                              mode=mode,
                                              arm_names=(arm_name,),
                                              interpolation_scheme=args.interpolation,
                                              interpolation_pixels=args.interpolation_pixels
                                              )

                # Calculate how much CPU time we used
                time_end = time.time()
                time_end_cpu = get_cpu_time(run_id)

                # Debugging
                # output_files[arm_name].write("# {}\n".format(str(rv_estimates)))

                # Write a line to the output data file
                output_files[arm_name].write("  {}\n".format(format_str).format(
                    "{:.2f}/{:.2f}".format(time_end - time_start, time_end_cpu - time_start_cpu),
                    "{:.1f}".format(test_spectrum.metadata.get("Teff", np.nan)),
                    "{:.1f}".format(stellar_parameters[0]),
                    "{:.3f}".format(test_spectrum.metadata.get("logg", np.nan)),
                    "{:.3f}".format(stellar_parameters[1]),
                    "{:.3f}".format(test_spectrum.metadata.get("[Fe/H]", np.nan)),
                    "{:.3f}".format(stellar_parameters[2]),
                    "{:.4f}".format(radial_velocity),
                    "{:.4f}".format(rv_mean / 1000),
                    "{:.4f}".format(rv_std_dev / 1000)
                ))

                # Make sure that output data file is always kept up to date
                output_files[arm_name].flush()
