#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Synthesize a handful of test stars using TurboSpectrum.
"""

import os
import re
import argparse
from os import path as os_path
import logging

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_specsynth import TurboSpectrum

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing spectra for some simple test stars")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output_library', required=False, default='demo_stars', dest='library')
parser.add_argument('--log-file', required=False, default='/tmp/turbospec_test.log', dest='log_to')
parser.add_argument('--line-lists-dir', required=False,
                    default=os_path.join(our_path, "..", "..", "fromBengt", "line_lists", "3700-9500"),
                    dest='lines_dir')
args = parser.parse_args()

logger.info("Synthesizing test stars with arguments <{}> <{}>".format(args.library, args.lines_dir))

# Set path to workspace where we create libraries of spectra
root_path = os_path.join(our_path, "..", "..")
workspace = os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Create new SpectrumLibrary
library_name = re.sub("/", "_", args.library)
library_path = os_path.join(workspace, library_name)
library = SpectrumLibrarySqlite(path=library_path, create=True, binary_spectra=False)

# Invoke a TurboSpectrum synthesizer instance
synthesizer = TurboSpectrum()

# Iterate over the spectra we're supposed to be synthesizing
with open(args.log_to, "w") as result_log:
    for t_eff in (3500, 4000, 4500, 5000, 5500, 6000):
        synthesizer.configure(t_eff=t_eff,
                              metallicity=0,
                              log_g=2,
                              lambda_min=3700,
                              lambda_max=9500,
                              lambda_delta=1,
                              line_list_paths=args.lines_dir
                              )

        # Make spectrum
        turbospectrum_out = synthesizer.synthesise()

        # Check for errors
        errors = turbospectrum_out['errors']
        if errors:
            result_log.write("{:.0f}: {}\n".format(t_eff, errors))
            result_log.flush()
            continue

        # Fetch filename of the spectrum we just generated
        filepath = os_path.join(turbospectrum_out["output_file"])

        # Insert spectrum into SpectrumLibrary
        metadata = {'Teff': t_eff, '[Fe/H]': 0, 'logg': 2}
        try:
            filename = os_path.split(filepath)[1]

            # First import continuum-normalised spectrum, which is in columns 1 and 2
            metadata['continuum_normalised'] = 1
            spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 1), binary=False)
            library.insert(spectra=spectrum, filenames=filename)

            # Then import version with continuum, which is in columns 1 and 3
            metadata['continuum_normalised'] = 0
            spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 2), binary=False)
            library.insert(spectra=spectrum, filenames=filename)
        except ValueError:
            result_log.write("{:.0f}: {}\n".format(t_eff, "Could not read bsyn output"))
            result_log.flush()
            continue

        result_log.write("{:.0f}: {}\n".format(t_eff, "OK"))
        result_log.flush()

# Close TurboSpectrum synthesizer instance
synthesizer.close()
