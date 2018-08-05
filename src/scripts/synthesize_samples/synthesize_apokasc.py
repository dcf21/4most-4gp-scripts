#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_apokasc.py>, but <./synthesize_apokasc.py> will not work.

"""
Take stellar parameters of the APOKASC training set and test sets, and synthesize spectrum using TurboSpectrum.
"""

import numpy as np
import logging
from astropy.table import Table
from lib.base_synthesizer import Synthesizer

# List of elements whose abundances we pass to TurboSpectrum
element_list = ("[C/H]", "[N/H]", "[O/H]", "[Na/H]", "[Mg/H]", "[Al/H]", "[Si/H]",
                "[Ca/H]", "[Ti/H]", "[Mn/H]", "[Co/H]", "[Ni/H]", "[Ba/H]", "[Sr/H]")

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing APOKASC grid of spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="apokasc_training_set",
                          logger=logger,
                          docstring=__doc__)

# Table supplies list of stars in the APOKASC training set, giving the stellar labels for each star in the training set
stellar_data = Table.read("../../4MOST_testspectra/trainingset_param.tab", format="ascii")

# Iterate over the spectra we're supposed to be synthesizing
star_list = []
for star in stellar_data:
    # Look up stellar parameters of the star we're about to synthesize
    metadata = synthesizer.astropy_row_to_dict(star)

    star_data = {
        "name": metadata["Starname"],
        "stellar_mass": metadata['Mass'] if 'Mass' in metadata else 1,
        "Teff": metadata['Teff'],
        "logg": metadata['logg'],
        "[Fe/H]": metadata['[Fe/H]'],
        "extra_metadata": {},
        "free_abundances": {},
        "input_data": {}
    }

    # Pass list of the abundances of individual elements to TurboSpectrum
    free_abundances = star_data["input_data"]
    for element in element_list:
        if element in metadata:
            if (not synthesizer.args.elements) or (element in synthesizer.args.elements.split(",")):
                chemical_symbol = element.split("/")[0][1:]
                free_abundances[chemical_symbol] = metadata[element]

    # If Sr and Ba are not already set, use Galactic trends
    if ('Sr' in free_abundances) and ('Ba' in free_abundances):
        if not (np.isfinite(free_abundances['Sr']) and np.isfinite(free_abundances['Ba'])):
            sr_dispersion = 0.2
            ba_dispersion = 0.15
            free_abundances['Sr'] = (np.random.normal(0, sr_dispersion) +
                                     (-0.1 + -0.52 * metadata['[Fe/H]']) + metadata['[Fe/H]'])
            free_abundances['Ba'] = np.random.normal(0, ba_dispersion) + metadata['[Fe/H]']
    star_list.append(star_data)

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
