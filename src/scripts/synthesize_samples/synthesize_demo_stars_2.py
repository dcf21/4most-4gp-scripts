#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_demo_stars_2.py>, but <./synthesize_demo_stars_2.py> will not work.

"""
Synthesize a handful of demo stars, e.g. the Sun, using TurboSpectrum.
"""

import logging
from lib.base_synthesizer import Synthesizer

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing spectra for some simple test stars")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="demo_stars_2",
                          logger=logger,
                          docstring=__doc__)

star_list = [
    {'name': "Sun", 'Teff': 5771.8, 'logg': 4.44, '[Fe/H]': 0, 'extra_metadata': {'set_id': 1}},
    {'name': "Giant", 'Teff': 4000, 'logg': 2, '[Fe/H]': 0, 'extra_metadata': {'set_id': 1}},
    {'name': "low_z", 'Teff': 5771.8, 'logg': 4.44, '[Fe/H]': -1, 'extra_metadata': {'set_id': 1}},
    {'name': "high_z", 'Teff': 5771.8, 'logg': 4.44, '[Fe/H]': 0.5, 'extra_metadata': {'set_id': 1}},
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
