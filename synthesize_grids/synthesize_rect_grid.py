#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_rect_grid.py>, but <./synthesize_rect_grid.py> will not work.

"""
Take a rectangular grid of [Teff, log_g, Fe/H] parameter values, and synthesize a spectrum at each
point in parameter space. Assume solar abundance ratios for all other elements.
"""

import logging
import numpy as np
import itertools
from base_synthesizer import Synthesizer

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing rectangular grid of spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="rect_grid",
                          logger=logger,
                          docstring=__doc__)

# Define limits and step size of rectangular grid
labels_to_vary = [
    {"name": "Teff", "min": 5600, "max": 6401, "step": 100},
    {"name": "logg", "min": 3.3, "max": 4.81, "step": 0.1},
    {"name": "[Fe/H]", "min": -1., "max": 0.21, "step": 0.1}
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
