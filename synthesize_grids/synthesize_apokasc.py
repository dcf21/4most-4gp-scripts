#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take stellar parameters of the APOKASC training set and test sets, and synthesize spectrum using TurboSpectrum.
"""

import os
import re
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
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output_library', required=False, default="APOKASC_trainingset_turbospec", dest="library")
parser.add_argument('--log-file', required=False, default="/tmp/turbospec_apokasc.log", dest="log_to")
parser.add_argument('--star_list', required=False, default="../../4MOST_testspectra/trainingset_param.tab",
                    dest="star_list")
parser.add_argument('--line-lists-dir', required=False, default=os_path.join(our_path, "..", ".."), dest="lines_dir")
parser.add_argument('--limit', required=False, default=None, type=int, dest="limit")
args = parser.parse_args()

logger.info("Synthesizing spectra with arguments <{}> <{}>".format(args.library, args.star_list))

# Set path to workspace where we create libraries of spectra
root_path = os_path.join(our_path, "..", "..")
workspace = os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Table supplies list of stars in the APOKASC training set, giving the stellar labels for each star in the training set
star_list = Table.read(args.star_list, format="ascii")

# Create new SpectrumLibrary
library_name = re.sub("/", "_", args.library)
library_path = os_path.join(workspace, library_name)
library = SpectrumLibrarySqlite(path=library_path, create=True)

# Invoke FourMost data class. Ensure that the spectra we produce are much higher resolution than 4MOST.
# We down-sample them later to whatever resolution we actually want.
FourMostData = FourMost()
lambda_min = FourMostData.bands["LRS"]["lambda_min"]
lambda_max = FourMostData.bands["LRS"]["lambda_max"]
line_lists_path = FourMostData.bands["LRS"]["line_lists_edvardsson"]
spectral_resolution = 50000

# Invoke a TurboSpectrum synthesizer instance
synthesizer = TurboSpectrum()
counter_output = 0

# Iterate over the spectra we're supposed to be synthesizing
with open(args.log_to, "w") as result_log:
    for star in star_list:
        counter_output += 1
        if (args.limit is not None) and (counter_output > args.limit):
            break
        metadata = astropy_row_to_dict(star)
        synthesizer.configure(lambda_min=lambda_min,
                              lambda_max=lambda_max,
                              lambda_delta=float(lambda_min) / spectral_resolution,
                              line_list_paths=[os_path.join(args.lines_dir, line_lists_path)],
                              stellar_mass=metadata['Mass'],
                              t_eff=metadata['Teff'],
                              metallicity=metadata['[Fe/H]'],
                              log_g=metadata['logg']
                              )

        # Pass list of the abundances of individual elements to TurboSpectrum
        free_abundances = {}
        for element in element_list:
            chemical_symbol = element.split("/")[0][1:]
            free_abundances[chemical_symbol] = metadata[element]

        # If Sr and Ba are not already set, use Galactic trends
        if not (np.isfinite(free_abundances['Sr']) and np.isfinite(free_abundances['Ba'])):
            sr_dispersion = 0.2
            ba_dispersion = 0.15
            free_abundances['Sr'] = np.random.normal(0, sr_dispersion) + \
                                    (-0.1 + -0.52 * metadata['[Fe/H]']) + metadata['[Fe/H]']
            free_abundances['Ba'] = np.random.normal(0, ba_dispersion) + metadata['[Fe/H]']

        # Set free abundances
        synthesizer.configure(free_abundances=free_abundances)

        # Make spectrum
        turbospectrum_out = synthesizer.synthesise()

        # Check for errors
        errors = turbospectrum_out['errors']
        if errors:
            result_log.write("{}: {}\n".format(metadata['Starname'], errors))
            result_log.flush()
            continue

        # Fetch filename of the spectrum we just generated
        filepath = os_path.join(turbospectrum_out["output_file"])

        # Insert spectrum into SpectrumLibrary
        try:
            spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, binary=False)
            filename = os_path.split(filepath)[1]
            library.insert(spectra=spectrum, filenames=filename)
        except ValueError:
            result_log.write("{}: {}\n".format(metadata['Starname'], "Could not read bsyn output"))
            result_log.flush()
            continue

        result_log.write("{}: {}\n".format(metadata['Starname'], "OK"))
        result_log.flush()

# Close TurboSpectrum synthesizer instance
synthesizer.close()
