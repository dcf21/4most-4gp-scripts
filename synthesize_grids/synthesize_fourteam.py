#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take parameters from Louise's email, and synthesize spectra using TurboSpectrum.
"""

import os
import re
import time
import hashlib
import argparse
import numpy as np
from os import path as os_path
import logging
import json

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_telescope_data import FourMost
from fourgp_specsynth import TurboSpectrum

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing fourteam spectra")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-library',
                    required=False,
                    default="turbospec_fourteam_sample",
                    dest="library",
                    help="Specify the name of the SpectrumLibrary we are to feed synthesized spectra into.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
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
                    default="/tmp/turbospec_saga_{}".format(pid),
                    dest="log_to",
                    help="Specify a log directory where we log our progress and configuration files.")
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

logger.info("Synthesizing four team stars with arguments <{}> <{}>".format(args.library, args.create))

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Open list of stars
star_list = [
    # Feh,Evol,Teff,logg
    [-2.00, 'MS', 7000, 4.40],
    [-2.00, 'TO', 7800, 4.05],
    [-2.00, 'SGB', 6600, 3.60],
    [-2.00, 'RGB', 5250, 2.40],
    [-1.50, 'MS', 6750, 4.40],
    [-1.50, 'TO', 7400, 4.05],
    [-1.50, 'SGB', 6400, 3.65],
    [-1.50, 'RGB', 5200, 2.40],
    [-1.00, 'MS', 6500, 4.40],
    [-1.00, 'TO', 6900, 4.05],
    [-1.00, 'SGB', 6200, 3.70],
    [-1.00, 'RGB', 5000, 2.40],
    [-0.50, 'MS', 6200, 4.40],
    [-0.50, 'TO', 6500, 4.05],
    [-0.50, 'SGB', 5900, 3.75],
    [-0.50, 'RGB', 4800, 2.40],
    [0.00, 'MS', 5900, 4.40],
    [0.00, 'TO', 6200, 4.05],
    [0.00, 'SGB', 5700, 3.85],
    [0.00, 'RGB', 4500, 2.40],
    [0.25, 'MS', 5700, 4.40],
    [0.25, 'TO', 5900, 4.05],
    [0.25, 'SGB', 5600, 3.90],
    [0.25, 'RGB', 4400, 2.40]
]

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
    for star_number, star in enumerate(star_list):
        star_name = "star_{:02d}".format(star_number)
        unique_id = hashlib.md5(os.urandom(32).encode("hex")).hexdigest()[:16]

        metadata = {
            "Starname": star_name,
            "uid": str(unique_id),
            "Teff": float(star[2]),
            "[Fe/H]": float(star[0]),
            "logg": float(star[3])
        }

        # User can specify that we should only do every nth spectrum, if we're running in parallel
        counter_output += 1
        if (args.limit > 0) and (counter_output > args.limit):
            break
        if (counter_output - args.skip) % args.every != 0:
            continue

        # Configure Turbospectrum with the stellar parameters of the next star
        synthesizer.configure(lambda_min=lambda_min,
                              lambda_max=lambda_max,
                              lambda_delta=float(lambda_min) / spectral_resolution,
                              line_list_paths=[os_path.join(args.lines_dir, line_lists_path)],
                              stellar_mass=1,
                              t_eff=float(star[2] + 1e-4),
                              metallicity=float(star[0] + 1e-6),
                              log_g=float(star[3] + 1e-6)
                              )

        # Pass list of the abundances of individual elements to TurboSpectrum
        free_abundances = {}
        synthesizer.configure(free_abundances=free_abundances)

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
            filename = "spectrum_{:08d}".format(counter_output)

            # First import continuum-normalised spectrum, which is in columns 1 and 2
            metadata['continuum_normalised'] = 1
            spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 1), binary=False)
            library.insert(spectra=spectrum, filenames=filename)

            # Then import version with continuum, which is in columns 1 and 3
            metadata['continuum_normalised'] = 0
            spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 2), binary=False)
            library.insert(spectra=spectrum, filenames=filename)
        except (ValueError, IndexError):
            result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                star_name, "Could not read bsyn output"))
            result_log.flush()
            continue

        # Update log file to show our progress
        result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                            star_name, "OK"))
        result_log.flush()

# Close TurboSpectrum synthesizer instance
synthesizer.close()