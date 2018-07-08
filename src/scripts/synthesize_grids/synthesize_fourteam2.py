#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_fourteam2.py>, but <./synthesize_fourteam2.py> will not work.

"""
Take parameters from Louise's email, and synthesize spectra using TurboSpectrum.
"""

import logging
from lib.base_synthesizer import Synthesizer

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing fourteam spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="fourteam2_sample",
                          logger=logger,
                          docstring=__doc__)

# Open list of stars
star_list = [
    {'[Fe/H]': -0.50, 'extra_metadata': {'evolution_state': 'TO'}, 'Teff': 6500, 'logg': 4.05},
    {'[Fe/H]': -0.50, 'extra_metadata': {'evolution_state': 'RGB'}, 'Teff': 4800, 'logg': 2.40},
    {'[Fe/H]': 0.00, 'extra_metadata': {'evolution_state': 'TO'}, 'Teff': 6200, 'logg': 4.05},
    {'[Fe/H]': 0.00, 'extra_metadata': {'evolution_state': 'RGB'}, 'Teff': 4500, 'logg': 2.40}
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
