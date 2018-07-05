#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python import_brani_grid.py>, but <./import_brani_grid.py> will not work.

"""
Take the 3x3x3 grid of template spectra used by Brani's RV code, and turn it into a SpectrumLibrary for use in
4MOST 4GP.

To run this script, you need to have a copy of the file <templates.npy> which is part of Brani's RV code.

The path to it is hard-coded below in the variable <template_spectra_path>, which you will need to change.
"""

import os
from os import path as os_path
import argparse
import numpy as np
import itertools
import logging

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum

# Path to where we find Brani's <4MOST_forward_modeling>
our_path = os_path.split(os_path.abspath(__file__))[0]
brani_code_path = os_path.join(our_path, "..", "..", "forwardModelling", "4MOST_forward_modeling")

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--brani-code-path',
                    required=False,
                    default=brani_code_path,
                    dest="brani_code_path",
                    help="Specify the path where we can find the original data files for Brani's RV code.")
args = parser.parse_args()

# Path to Brani's template wavelength grid and templates
wavelength_raster_path = os_path.join(args.brani_code_path, "LAMBDA_RAV.DAT")
template_spectra_path = os_path.join(args.brani_code_path, "templates.npy")

# Start logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Importing grid of template spectra for Brani's RV code")

# Set path to workspace where we create libraries of spectra
workspace = os_path.join(our_path, "..", "workspace")
target_library_name = "brani_rv_grid"
os.system("mkdir -p {}".format(workspace))

# Load pickled collection of templates
wavelength_raster = np.loadtxt(wavelength_raster_path)
flux_templates = np.load(template_spectra_path)

# logger.info("Full wavelength array shape: {}".format(wavelength_raster.shape))
# logger.info("Flux template array shape: {}".format(flux_templates.shape))

# Filter wavelength range
wavelength_filter = (wavelength_raster > 3670) & (wavelength_raster < 9530)
wavelength_raster = wavelength_raster[wavelength_filter]

# logger.info("After filtering, wavelength array shape: {}".format(wavelength_raster.shape))

# The stellar parameters which each grid axis samples are not specified in Brani's <templates.npy> file.
# They are as follows...
grid_axes = [["Teff", (4000, 8250, 250)],
             ["Fe/H", (0.5, 3.0, 0.5)],
             ["log_g", (1.5, 5.5, 0.5)]
             ]

grid_axis_values = [np.arange(axis[1][0], axis[1][1], axis[1][2]) for axis in grid_axes]
grid_axis_indices = [range(int((axis[1][1] - axis[1][0]) / axis[1][2])) for axis in grid_axes]
grid_axis_index_combinations = itertools.product(*grid_axis_indices)

# Turn Brani's set of templates into a SpectrumLibrary with path specified above
library_path = os_path.join(workspace, target_library_name)
library = SpectrumLibrarySqlite(path=library_path, create=True)

# Brani's template spectra do not have any error vectors associated with them
errors_dummy = np.zeros_like(wavelength_raster)

# Import each template spectrum in turn
for i, axis_indices in enumerate(grid_axis_index_combinations):
    filename = "template{:06d}".format(i)
    metadata = {"Starname": filename}
    item = flux_templates
    for axis_counter, index in enumerate(axis_indices):
        metadata_key = grid_axes[axis_counter][0]
        metadata_value = grid_axis_values[axis_counter][index]
        metadata[metadata_key] = metadata_value
        metadata[metadata_key + "_index"] = index
        item = item[index]

    # Turn data into a Spectrum object
    spectrum = Spectrum(wavelengths=wavelength_raster,
                        values=item,
                        value_errors=errors_dummy,
                        metadata=metadata)

    # Import spectrum into our SpectrumLibrary
    library.insert(spectra=spectrum, filenames=filename)
