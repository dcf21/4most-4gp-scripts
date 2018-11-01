#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_rv_fitting_grid.py>, but <./synthesize_rv_fitting_grid.py> will not work.

"""
Use this is synthesise a coarse grid of templates in [Teff, log_g, Fe/H] parameter space, used for doing cross
correlation when fitting RVs.

Take a rectangular grid of [Teff, log_g, Fe/H] parameter values, and synthesize a spectrum at each
point in parameter space. Assume solar abundance ratios for all other elements.
"""

import itertools
import logging

import numpy as np
from lib.base_synthesizer import Synthesizer

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing a coarse rectangular grid of spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="rv_templates",
                          logger=logger,
                          docstring=__doc__)

# Define limits and step size of rectangular grid
labels_to_vary = [
    {"name": "Teff", "min": 4000, "max": 8001, "step": 500},
    {"name": "logg", "min": 1.5, "max": 4.51, "step": 1.0},
    {"name": "[Fe/H]", "min": -1.5, "max": 0.51, "step": 1.0}
]

# Create a list of all of the points in this grid
label_values = [np.arange(item['min'], item['max'], item['step']) for item in labels_to_vary]
label_combinations = itertools.product(*label_values)

# Turn into a list of stellar parameters
star_list = []
for grid_point in label_combinations:
    star_name = "rect_grid"
    item = {}
    for index, label in enumerate(labels_to_vary):
        x = float(grid_point[index]) + 1e-4
        item[label['name']] = x
        star_name += "_{:.1f}".format(x)
    item["name"] = str(star_name)
    star_list.append(item)

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
