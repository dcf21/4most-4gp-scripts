#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Synthesize a handful of test stars using TurboSpectrum.
"""

import logging
from base_synthesizer import Synthesizer

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing spectra for some simple test stars")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="demo_stars",
                          logger=logger)

star_list = [
    {'name': "Sun", 'Teff': 5771.8, 'logg': 4.44, '[Fe/H]': 0, 'extra_metadata': {'set_id': 1}},
    {'name': "Red_clump", 'Teff': 5000, 'logg': 3, '[Fe/H]': 0, 'extra_metadata': {'set_id': 1}},
    {'name': "Dwarf", 'Teff': 6000, 'logg': 4, '[Fe/H]': -0.8, 'extra_metadata': {'set_id': 1}},
    {'name': "test_3500", 'Teff': 3500, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
    {'name': "test_4000", 'Teff': 4000, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
    {'name': "test_4500", 'Teff': 4500, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
    {'name': "test_5000", 'Teff': 5000, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
    {'name': "test_5500", 'Teff': 5500, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
    {'name': "test_6000", 'Teff': 6000, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
    {'name': "test_6500", 'Teff': 6500, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
    {'name': "test_7000", 'Teff': 7000, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 0}},
]

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
