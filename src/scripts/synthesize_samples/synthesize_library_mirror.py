#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_library_mirror.py>, but <./synthesize_library_mirror.py> will not work.

"""
Take the stellar parameters of the stars in a spectrum library, and use Turbospectrum to create synthetic spectra with
matching parameters. We use this to test how well Turbospectrum matches what real spectra look like.
"""

import logging
import re
from lib.base_synthesizer import Synthesizer

from fourgp_speclib import SpectrumLibrarySqlite

# Input library we are to act on
input_library = "pepsi_4fs_hrs"

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Creating synthetic versions of stars from <{}>".format(input_library))

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="pepsi_synthetic",
                          logger=logger,
                          docstring=__doc__)

star_list = []

# Open input spectrum library
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=input_library,
                                                workspace=synthesizer.workspace,
                                                extra_constraints={"continuum_normalised": 1}
                                                )

# Get a list of the spectrum IDs which we were returned
input_library, input_spectra_ids, input_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

# Loop over input spectra
for input_spectrum_id in input_spectra_ids:
    logger.info("Working on <{}>".format(input_spectrum_id['filename']))
    # Open Spectrum data from disk
    input_spectrum_array = input_library.open(ids=input_spectrum_id['specId'])

    # Turn SpectrumArray object into a Spectrum object
    input_spectrum = input_spectrum_array.extract_item(0)
    metadata = input_spectrum.metadata

    # Ignore stars without basic metadata
    if 'Teff' not in metadata:
        logger.info("Insufficient metadata")
        continue

    # Star descriptor
    star_descriptor = {
        'name': metadata['Starname'],
        'Teff': metadata['Teff'],
        'logg': metadata['logg'],
        '[Fe/H]': metadata['[Fe/H]'],
        'free_abundances': {},
        'extra_metadata': {}
    }

    # Insert manually set abundances
    for key, value in metadata.iteritems():
        test = re.match("\[(.*)/H\]", key)
        if test is not None:
            element = test.group(1)
            star_descriptor['free_abundances'][element] = value

    # Add star to list of those to synthesise
    star_list.append(star_descriptor)

# Pass list of stars to synthesizer
synthesizer.set_star_list(star_list)

# Output data into sqlite3 db
synthesizer.dump_stellar_parameters_to_sqlite()

# Create new SpectrumLibrary
synthesizer.create_spectrum_library()

# Iterate over the spectra we're supposed to be synthesizing
synthesizer.do_synthesis()

# Close TurboSpectrum synthesizer instance
synthesizer.clean_up()
