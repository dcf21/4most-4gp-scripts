#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take parameters of synthetic dwarf sample emailed by Ross on 20 March 2018, and synthesise them.
"""

import logging
from base_synthesizer import Synthesizer

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing synthetic_dwarf_sample spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="synthetic_dwarf_sample",
                          logger=logger,
                          docstring=__doc__)

# Table supplies list of abundances for the stars
f = open("../../downloads/ross_synthetic_dwarf_sample.dat").readlines()

# Loop over stars extracting stellar parameters from FITS file
star_list = []
for star_index, line in enumerate(f):
    words = line.split()
    fe_h = float(words[2])
    star_list_item = {
        "name": "star_{:05d}".format(star_index),
        "Teff": float(words[0]),
        "[Fe/H]": fe_h,
        "logg": float(words[1]),
        "extra_metadata": {},
        "free_abundances": {
            "Ca": float(words[3]) + fe_h,
            "Mg": float(words[4]) + fe_h,
            "Ti": float(words[5]) + fe_h,
            "Si": float(words[6]) + fe_h,
            "Na": float(words[7]) + fe_h,
            "Ni": float(words[8]) + fe_h,
            "Cr": float(words[9]) + fe_h,
        },
        "input_data": {}
    }
    star_list.append(star_list_item)

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
