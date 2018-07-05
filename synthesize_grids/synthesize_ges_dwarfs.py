#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_ges_dwarfs.py>, but <./synthesize_ges_dwarfs.py> will not work.

"""
Take stellar parameters of GES dwarf stars and synthesize spectra using TurboSpectrum.
"""

import numpy as np
import logging
import json
from astropy.io import fits
from lib.base_synthesizer import Synthesizer

# List of elements whose abundances we pass to TurboSpectrum
# Elements with neutral abundances, e.g. LI1
element_list = (
    "He", "Li", "C", "O", "Ne", "Na", "Mg", "Al", "Si", "S", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Co", "Ni", "Cu", "Zn",
    "Sr", "Y", "Zr", "Nb", "Mo", "Ru")

# Elements with ionised abundances, e.g. N2
element_list_ionised = ("N", "Ba", "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Dy")

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing GES dwarf spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="ges_dwarf_sample",
                          logger=logger,
                          docstring=__doc__)

# Table supplies list of abundances for GES stars
f = fits.open("../../downloads/GES_iDR5_WG15_Recommended.fits")
ges = f[1].data
ges_fields = ges.names

# Obtain solar abundances, needed to convert values in file into solar units
sun_id = np.where(ges.OBJECT == 'Sun_Benchmarks_BordeauxLib3     ')[0]

# Filter objects on SNR
min_SNR = 50
selection = np.where((ges.SNR > min_SNR) & (ges.REC_WG == 'WG11') & (ges.LOGG > 3.5))[0]
stellar_data = ges[selection]

# Loop over stars extracting stellar parameters from FITS file
star_list = []
for star_index in range(len(stellar_data)):
    star_list_item = {
        "name": stellar_data.CNAME[star_index],
        "Teff": float(stellar_data.TEFF[star_index]),
        "[Fe/H]": float(stellar_data.FEH[star_index]),
        "logg": float(stellar_data.LOGG[star_index]),
        "extra_metadata": {
            "[alpha/Fe]": float(stellar_data.ALPHA_FE[star_index])
        },
        "free_abundances": {},
        "input_data": {}
    }

    # Pass list of the abundances of individual elements to TurboSpectrum
    free_abundances = star_list_item["free_abundances"]
    for elements, ionisation_state in ((element_list, 1), (element_list_ionised, 2)):
        for element in elements:
            if (not synthesizer.args.elements) or (element in synthesizer.args.elements.split(",")):
                fits_field_name = "{}{}".format(element.upper(), ionisation_state)

                # Normalise abundance of element to solar
                abundance = stellar_data[fits_field_name][star_index] - ges[fits_field_name][sun_id]

                if np.isfinite(abundance):
                    free_abundances[element] = float(abundance)

    # Propagate all ionisation states into metadata
    metadata = star_list_item["extra_metadata"]
    for element in element_list:
        abundances_all = []
        for ionisation_state in range(1, 5):
            fits_field_name = "{}{}".format(element.upper(), ionisation_state)
            if fits_field_name in ges_fields:
                abundance = stellar_data[fits_field_name][star_index] - ges[fits_field_name][sun_id]
                abundances_all.append(float(abundance))
            else:
                abundances_all.append(None)
        metadata["[{}/H]_ionised_states".format(element)] = json.dumps(abundances_all)

    # Propagate all input fields from the FITS file into <input_data>
    input_data = star_list_item["input_data"]
    for col_name in ges_fields:
        if col_name == "CNAME":
            continue
        value = stellar_data[col_name][star_index]

        if ges.dtype[col_name].type is np.string_:
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
