#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_galah.py>, but <./synthesize_galah.py> will not work.

"""
Take parameters of GALAH sample of stars emailed by Karin on 30 Oct 2017, and synthesize spectra using
TurboSpectrum.
"""

import numpy as np
import logging
from astropy.io import fits
from lib.base_synthesizer import Synthesizer

# List of elements whose abundances we pass to TurboSpectrum
element_list = (
    'Al', 'Ba', 'C', 'Ca', 'Ce', 'Co', 'Cr', 'Cu', 'Eu', 'K', 'La', 'Li', 'Mg', 'Mn', 'Mo', 'Na', 'Nd', 'Ni', 'O',
    'Rb', 'Ru', 'Sc', 'Si', 'Sm', 'Sr', 'Ti', 'V', 'Y', 'Zn', 'Zr'
)

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing GALAH sample spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="galah_sample_v2",
                          logger=logger,
                          docstring=__doc__)

# Table supplies list of abundances for GES stars
f = fits.open("../../downloads/GALAH_trainingset_4MOST_errors.fits")
galah_stars = f[1].data
galah_fields = galah_stars.names
# print galah_fields  # To print a list of available parameters

"""
>>> print galah_fields
['SNR', 'Teff_sme', 'e_Teff_sme', 'Logg_sme', 'e_Logg_sme', 'Feh_sme', 'e_Feh_sme', 'Vmic_sme', 'e_Vmic_sme',
 'Vsini_sme', 'e_Vsini_sme', 'Ak', 'Alpha_fe_sme', 'e_Alpha_fe_sme', 'Al_abund_sme', 'e_Al_abund_sme',
 'flag_Al_abund_sme', 'Ba_abund_sme', 'e_Ba_abund_sme', 'flag_Ba_abund_sme', 'C_abund_sme', 'e_C_abund_sme',
 'flag_C_abund_sme', 'Ca_abund_sme', 'e_Ca_abund_sme', 'flag_Ca_abund_sme', 'Ce_abund_sme', 'e_Ce_abund_sme',
 'flag_Ce_abund_sme', 'Co_abund_sme', 'e_Co_abund_sme', 'flag_Co_abund_sme', 'Cr_abund_sme', 'e_Cr_abund_sme',
 'flag_Cr_abund_sme', 'Cu_abund_sme', 'e_Cu_abund_sme', 'flag_Cu_abund_sme', 'Eu_abund_sme', 'e_Eu_abund_sme',
 'flag_Eu_abund_sme', 'K_abund_sme', 'e_K_abund_sme', 'flag_K_abund_sme', 'La_abund_sme', 'e_La_abund_sme',
 'flag_La_abund_sme', 'Li_abund_sme', 'e_Li_abund_sme', 'flag_Li_abund_sme', 'Mg_abund_sme', 'e_Mg_abund_sme',
 'flag_Mg_abund_sme', 'Mn_abund_sme', 'e_Mn_abund_sme', 'flag_Mn_abund_sme', 'Mo_abund_sme', 'e_Mo_abund_sme',
 'flag_Mo_abund_sme', 'Na_abund_sme', 'e_Na_abund_sme', 'flag_Na_abund_sme', 'Nd_abund_sme', 'e_Nd_abund_sme',
 'flag_Nd_abund_sme', 'Ni_abund_sme', 'e_Ni_abund_sme', 'flag_Ni_abund_sme', 'O_abund_sme', 'e_O_abund_sme',
 'flag_O_abund_sme', 'Rb_abund_sme', 'e_Rb_abund_sme', 'flag_Rb_abund_sme', 'Ru_abund_sme', 'e_Ru_abund_sme',
 'flag_Ru_abund_sme', 'Sc_abund_sme', 'e_Sc_abund_sme', 'flag_Sc_abund_sme', 'Si_abund_sme', 'e_Si_abund_sme',
 'flag_Si_abund_sme', 'Sm_abund_sme', 'e_Sm_abund_sme', 'flag_Sm_abund_sme', 'Sr_abund_sme', 'e_Sr_abund_sme',
 'flag_Sr_abund_sme', 'Ti_abund_sme', 'e_Ti_abund_sme', 'flag_Ti_abund_sme', 'V_abund_sme', 'e_V_abund_sme',
 'flag_V_abund_sme', 'Y_abund_sme', 'e_Y_abund_sme', 'flag_Y_abund_sme', 'Zn_abund_sme', 'e_Zn_abund_sme',
 'flag_Zn_abund_sme', 'Zr_abund_sme', 'e_Zr_abund_sme', 'flag_Zr_abund_sme']
"""

# Loop over stars extracting stellar parameters from FITS file
star_list = []
for star_index in range(len(galah_stars)):
    fe_abundance = float(galah_stars.Feh_sme[star_index])

    star_list_item = {
        "name": "star_{:08d}".format(star_index),
        "Teff": float(galah_stars.Teff_sme[star_index]),
        "[Fe/H]": fe_abundance,
        "logg": float(galah_stars.Logg_sme[star_index]),
        "extra_metadata": {},
        "free_abundances": {},
        "input_data": {}
    }

    # Pass list of the abundances of individual elements to TurboSpectrum
    free_abundances = star_list_item["free_abundances"]
    metadata = star_list_item["extra_metadata"]
    for element in element_list:
        if (not synthesizer.args.elements) or (element in synthesizer.args.elements.split(",")):
            fits_field_name = "{}_abund_sme".format(element)

            # Abundance is specified as [X/Fe]. Convert to [X/H]
            abundance = galah_stars[fits_field_name][star_index] + fe_abundance

            if np.isfinite(abundance):
                free_abundances[element] = float(abundance)
                metadata["flag_{}".format(element)] = float(galah_stars["flag_{}_abund_sme".format(element)][star_index])

    # Propagate all input fields from the FITS file into <input_data>
    input_data = star_list_item["input_data"]
    for col_name in galah_fields:
        value = galah_stars[col_name][star_index]

        if galah_stars.dtype[col_name].type is np.string_:
            typed_value = str(value)
        else:
            typed_value = float(value)

        input_data[col_name] = typed_value
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
