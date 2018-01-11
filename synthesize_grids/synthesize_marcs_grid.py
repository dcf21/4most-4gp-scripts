#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take the [Teff, log_g, Fe/H] parameter values in the MARCs grid of model atmospheres, and synthesize a spectrum at each
point in parameter space. Assume solar abundance ratios for all other elements.
"""

import os
import re
import time
import argparse
from os import path as os_path
import logging
import json
import glob

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_telescope_data import FourMost
from fourgp_specsynth import TurboSpectrum

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing MARCS grid of spectra")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-library',
                    required=False,
                    default="turbospec_marcs_grid",
                    dest="library",
                    help="Specify the name of the SpectrumLibrary we are to feed synthesized spectra into.")
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
parser.add_argument('--log-dir',
                    required=False,
                    default="/tmp/turbospec_marcs_grid_{}".format(pid),
                    dest="log_to",
                    help="Specify a log directory where we log our progress and configuration files.")
parser.add_argument('--marcs_path',
                    required=False,
                    default="../../fromBengt/marcs_grid",
                    dest="marcs_path",
                    help="Specify the path to the grid of MARCS models we use to specify raster of stellar parameters.")
parser.add_argument('--line-lists-dir',
                    required=False,
                    default=root_path,
                    dest="lines_dir",
                    help="Specify a directory where line lists for TurboSpectrum can be found.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where Turbospectrum and Interpol packages are installed.")
parser.add_argument('--every',
                    required=False,
                    default=1,
                    type=int,
                    dest="every",
                    help="Only process every nth spectrum. "
                         "This is useful when parallelising this script across multiple processes.")
parser.add_argument('--skip',
                    required=False,
                    default=0,
                    type=int,
                    dest="skip",
                    help="Skip n spectra before starting to process every nth. "
                         "This is useful when parallelising this script across multiple processes.")
parser.add_argument('--limit',
                    required=False,
                    default=0,
                    type=int,
                    dest="limit",
                    help="Only process a maximum of n spectra.")
args = parser.parse_args()

logger.info("Synthesizing MARCS grid with arguments <{}> <{}>".format(args.library, args.marcs_path))

# Set path to workspace where we create libraries of spectra
workspace = os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))


def fetch_marcs_grid(marcs_grid_path):
    """
    Get a list of all of the MARCS models we have.

    :return:
        None
    """

    pattern = r"([sp])(\d\d\d\d)_g(....)_m(...)_t(..)_(..)_z(.....)_" \
              r"a(.....)_c(.....)_n(.....)_o(.....)_r(.....)_s(.....).mod"

    marcs_values = {
        "temperature": [],
        "log_g": [],
        "metallicity": []
    }

    marcs_models = glob.glob(os_path.join(marcs_grid_path, "*"))
    for item in marcs_models:

        # Extract model parameters from .mod filename
        filename = os_path.split(item)[1]
        re_test = re.match(pattern, filename)
        assert re_test is not None, "Could not parse MARCS model filename <{}>".format(filename)

        try:
            model = {
                "spherical": re_test.group(1),
                "temperature": float(re_test.group(2)),
                "log_g": float(re_test.group(3)),
                "mass": float(re_test.group(4)),
                "turbulence": float(re_test.group(5)),
                "model_type": re_test.group(6),
                "metallicity": float(re_test.group(7)),
                "a": float(re_test.group(8)),
                "c": float(re_test.group(9)),
                "n": float(re_test.group(10)),
                "o": float(re_test.group(11)),
                "r": float(re_test.group(12)),
                "s": float(re_test.group(13))
            }
        except ValueError:
            logger.error("Could not parse MARCS model filename <{}>".format(filename))
            raise

        # Keep a list of all of the parameter values we've seen
        for parameter, value in model.iteritems():
            if parameter in marcs_values:
                if value not in marcs_values[parameter]:
                    marcs_values[parameter].append(value)

    # Sort model parameter values into order
    for parameter in marcs_values:
        marcs_values[parameter].sort()

    return marcs_values


parameter_values = fetch_marcs_grid(args.marcs_path)
for key, value in parameter_values.iteritems():
    logger.info("We have {:6d} values for parameter <{}>: {}".format(len(value), key, value))

# Create new SpectrumLibrary
library_name = re.sub("/", "_", args.library)
library_path = os_path.join(workspace, library_name)
library = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Invoke FourMost data class. Ensure that the spectra we produce are much higher resolution than 4MOST.
# We down-sample them later to whatever resolution we actually want.
FourMostData = FourMost()
lambda_min = FourMostData.bands["LRS"]["lambda_min"]
lambda_max = FourMostData.bands["LRS"]["lambda_max"]
line_lists_path = FourMostData.bands["LRS"]["line_lists_edvardsson"]
spectral_resolution = 50000

# Invoke a TurboSpectrum synthesizer instance
synthesizer = TurboSpectrum(
    turbospec_path=os_path.join(args.binary_path, "turbospectrum-15.1/exec-gf-v15.1"),
    interpol_path=os_path.join(args.binary_path, "interpol_marcs"),
    line_list_paths=[os_path.join(args.lines_dir, line_lists_path)],
    marcs_grid_path=os_path.join(args.binary_path, "fromBengt/marcs_grid"))
counter_output = 0

# Start making log output
os.system("mkdir -p {}".format(args.log_to))
logfile = os.path.join(args.log_to, "synthesis.log")

# Iterate over the spectra we're supposed to be synthesizing
with open(logfile, "w") as result_log:
    for i1, t_eff in enumerate(parameter_values['temperature']):
        for i2, log_g in enumerate(parameter_values['log_g']):
            for i3, fe_h in enumerate(parameter_values['metallicity']):
                # User can specify that we should only do every nth spectrum, if we're running in parallel
                counter_output += 1
                if (args.limit > 0) and (counter_output > args.limit):
                    break
                if (counter_output - args.skip) % args.every != 0:
                    continue

                # Apply a small perturbation because the MARCs model interpolator seems to prefer it that way
                t_eff = min(t_eff + 10, 7990)
                log_g = min(log_g + 0.01, 5.49)
                fe_h = min(fe_h + 0.01, 0.99)

                star_name = "marcs_{:02d}_{:02d}_{:02d}".format(i1, i2, i3)

                metadata = {
                    "Starname": str(star_name),
                    "Teff": float(t_eff),
                    "[Fe/H]": float(fe_h),
                    "logg": float(log_g)
                }

                # Configure Turbospectrum with the stellar parameters of the next star
                synthesizer.configure(lambda_min=lambda_min,
                                      lambda_max=lambda_max,
                                      lambda_delta=float(lambda_min) / spectral_resolution,
                                      line_list_paths=[os_path.join(args.lines_dir, line_lists_path)],
                                      stellar_mass=1,
                                      t_eff=float(t_eff),
                                      metallicity=float(fe_h),
                                      log_g=float(log_g)
                                      )

                # Make spectrum
                time_start = time.time()
                turbospectrum_out = synthesizer.synthesise()
                time_end = time.time()

                # Log synthesizer status
                logfile_this = os.path.join(args.log_to, "{}.log".format(star_name))
                open(logfile_this, "w").write(json.dumps(turbospectrum_out))

                # Check for errors
                errors = turbospectrum_out['errors']
                if errors:
                    result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                        star_name, errors))
                    result_log.flush()
                    continue

                # Fetch filename of the spectrum we just generated
                filepath = os_path.join(turbospectrum_out["output_file"])

                # Insert spectrum into SpectrumLibrary
                try:
                    # First import continuum-normalised spectrum, which is in columns 1 and 2
                    metadata['continuum_normalised'] = 1
                    spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 1), binary=False)
                    library.insert(spectra=spectrum, filenames=star_name)

                    # Then import version with continuum, which is in columns 1 and 3
                    metadata['continuum_normalised'] = 0
                    spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 2), binary=False)
                    library.insert(spectra=spectrum, filenames=star_name)
                except (ValueError, IndexError):
                    result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                        star_name, "Could not read bsyn output"))
                    result_log.flush()
                    continue

                # Update log file to show our progress
                result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                    star_name, "OK"))
                result_log.flush()  # Close TurboSpectrum synthesizer instance
synthesizer.close()
