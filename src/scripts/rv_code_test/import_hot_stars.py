#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python import_hot_stars.py>, but <./resample_cross_correlation_grid.py> will not work.

"""
Take the directories of ASCII hot star spectra supplied by Joachim Bestenlehner, and turn them into 4GP
spectrum libraries.
"""

import hashlib
import logging
import os
from os import path as os_path

import numpy as np
from fourgp_speclib import Spectrum, SpectrumLibrarySqlite

src_dir = "../../../../hot_stars"

# Set up logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info("Importing hot star spectra")

# Workspace directory
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "../../../workspace")

# Create output spectrum libraries
library_path = os_path.join(workspace, "hot_star_templates")
output_library_templates = SpectrumLibrarySqlite(path=library_path, create=True)

library_path = os_path.join(workspace, "hot_star_test_objects")
output_library_test_objects = SpectrumLibrarySqlite(path=library_path, create=True)

# Template spectra
for line in open(os_path.join(src_dir, "sp_templates.txt")):
    line = line.strip()

    if line == "" or line.startswith("#"):
        continue

    words = line.split()
    unique_id = hashlib.md5(os.urandom(32)).hexdigest()[:16]
    metadata = {
        "Teff": float(words[1]),
        "logg": float(words[2]),
        "Mdot": float(words[3]),
        "[Fe/H]": 0,
        "uid": unique_id,
        "Starname": "hot_star_{:03d}".format(int(words[0])),
        "continuum_normalised": 1
    }

    filename = os_path.join(src_dir, "templates", "{:02d}_template.ascii".format(int(words[0])))

    wavelengths = np.asarray([float(x.split()[0]) for x in open(filename)])
    values = np.asarray([float(x.split()[1]) for x in open(filename)])
    spectrum = Spectrum(wavelengths=wavelengths,
                        values=values,
                        value_errors=np.zeros_like(wavelengths),
                        metadata=metadata)

    output_library_templates.insert(spectra=spectrum, metadata_list=[{'continuum_normalised': 0}])
    output_library_templates.insert(spectra=spectrum, metadata_list=[{'continuum_normalised': 1}])

# Test spectra
for line in open(os_path.join(src_dir, "sp_test-sample.txt")):
    line = line.strip()

    if line == "" or line.startswith("#"):
        continue

    words = line.split()
    unique_id = hashlib.md5(os.urandom(32)).hexdigest()[:16]
    metadata = {
        "Teff": float(words[1]),
        "logg": float(words[2]),
        "Mdot": float(words[3]),
        "[Fe/H]": 0,
        "uid": unique_id,
        "Starname": "hot_star_{:03d}".format(int(words[0])),
        "continuum_normalised": 1
    }

    filename = os_path.join(src_dir, "test_sample", "{:03d}_test.ascii".format(int(words[0])))

    wavelengths = np.asarray([float(x.split()[0]) for x in open(filename)])
    values = np.asarray([float(x.split()[1]) for x in open(filename)])
    spectrum = Spectrum(wavelengths=wavelengths,
                        values=values,
                        value_errors=np.zeros_like(wavelengths),
                        metadata=metadata)

    output_library_templates.insert(spectra=spectrum, metadata_list=[{'continuum_normalised': 0}])
    output_library_templates.insert(spectra=spectrum, metadata_list=[{'continuum_normalised': 1}])
