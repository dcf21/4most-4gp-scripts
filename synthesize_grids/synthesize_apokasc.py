#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take stellar parameters of the APOKASC training set and test sets, and synthesize spectrum using TurboSpectrum.
"""

import os
import re
import time
import argparse
import numpy as np
from os import path as os_path
import logging
from astropy.table import Table

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_telescope_data import FourMost
from fourgp_specsynth import TurboSpectrum

# List of elements whose abundances we pass to TurboSpectrum
element_list = ("[C/H]", "[N/H]", "[O/H]", "[Na/H]", "[Mg/H]", "[Al/H]", "[Si/H]",
                "[Ca/H]", "[Ti/H]", "[Mn/H]", "[Co/H]", "[Ni/H]", "[Ba/H]", "[Sr/H]")


# Convenience function, coz it would've been too helpful for astropy to actually provide dictionary access to rows
def astropy_row_to_dict(x):
    return dict([(i, x[i]) for i in x.columns])


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing APOKASC grid of spectra")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-library',
                    required=False,
                    default="turbospec_apokasc_training_set",
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
                    default="/tmp/turbospec_apokasc_{}".format(pid),
                    dest="log_to",
                    help="Specify a log directory where we log our progress and configuration files.")
parser.add_argument('--star-list',
                    required=False,
                    default="../../4MOST_testspectra/trainingset_param.tab",
                    dest="star_list",
                    help="Specify an ASCII table which lists the stellar parameters of the stars to be synthesized.")
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

logger.info("Synthesizing spectra with arguments <{}> <{}>".format(args.library, args.star_list))

# Set path to workspace where we create libraries of spectra
workspace = os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Table supplies list of stars in the APOKASC training set, giving the stellar labels for each star in the training set
star_list = Table.read(args.star_list, format="ascii")

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

# Iterate over the spectra we're supposed to be synthesizing
with open(args.log_to, "w") as result_log:
    for star in star_list:
        # User can specify that we should only do every nth spectrum, if we're running in parallel
        counter_output += 1
        if (args.limit > 0) and (counter_output > args.limit):
            break
        if (counter_output - args.skip) % args.every != 0:
            continue

        # Look up stellar parameters of the star we're about to synthesize
        metadata = astropy_row_to_dict(star)
        star_name = metadata["Starname"]
        stellar_mass = 1  # If mass of star is not specified, default to 1 solar mass
        if 'Mass' in metadata:
            stellar_mass = metadata['Mass']

        # Configure Turbospectrum with the stellar parameters of the next star
        synthesizer.configure(lambda_min=lambda_min,
                              lambda_max=lambda_max,
                              lambda_delta=float(lambda_min) / spectral_resolution,
                              line_list_paths=[os_path.join(args.lines_dir, line_lists_path)],
                              stellar_mass=stellar_mass,
                              t_eff=metadata['Teff'],
                              metallicity=metadata['[Fe/H]'],
                              log_g=metadata['logg']
                              )

        # Pass list of the abundances of individual elements to TurboSpectrum
        free_abundances = {}
        for element in element_list:
            if element in metadata:
                chemical_symbol = element.split("/")[0][1:]
                free_abundances[chemical_symbol] = metadata[element]

        # If Sr and Ba are not already set, use Galactic trends
        if ('Sr' in free_abundances) and ('Ba' in free_abundances):
            if not (np.isfinite(free_abundances['Sr']) and np.isfinite(free_abundances['Ba'])):
                sr_dispersion = 0.2
                ba_dispersion = 0.15
                free_abundances['Sr'] = np.random.normal(0, sr_dispersion) + \
                                        (-0.1 + -0.52 * metadata['[Fe/H]']) + metadata['[Fe/H]']
                free_abundances['Ba'] = np.random.normal(0, ba_dispersion) + metadata['[Fe/H]']

        # Set free abundances
        synthesizer.configure(free_abundances=free_abundances)

        # Make spectrum
        time_start = time.time()
        turbospectrum_out = synthesizer.synthesise()
        time_end = time.time()

        # Check for errors
        errors = turbospectrum_out['errors']
        if errors:
            result_log.write("[{}] {:6s} sec {}: {}\n".format(time.asctime(), time_end-time_start,
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
            result_log.write("[{}] {:6s} sec {}: {}\n".format(time.asctime(), time_end-time_start,
                                                              star_name, "Could not read bsyn output"))
            result_log.flush()
            continue

        # Update log file to show our progress
        result_log.write("[{}] {:6s} sec {}: {}\n".format(time.asctime(), time_end-time_start,
                                                          star_name, "OK"))
        result_log.flush()

# Close TurboSpectrum synthesizer instance
synthesizer.close()
