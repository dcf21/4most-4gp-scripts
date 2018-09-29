#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_ahm2017_perturbed.py>, but <./synthesize_ahm2017_perturbed.py> will not work.

"""
Take parameters of GES sample of stars proposed by Georges at the AHM2017 in Lyon, and synthesize spectra using
TurboSpectrum.
"""

import logging
import random

import numpy as np
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
logger.info("Synthesizing AHM2017 spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="ahm2017_perturbed",
                          logger=logger,
                          docstring=__doc__)

# Table supplies list of abundances for GES stars
f = fits.open("../../downloads/GES_iDR5_WG15_Recommended.fits")
ges = f[1].data
ges_fields = ges.names

# Obtain solar abundances, needed to convert values in file into solar units
sun_id = np.where(ges.OBJECT == 'Sun_Benchmarks_BordeauxLib3     ')[0]

# Filter objects as specified by Georges at Lyon meeting
selection = np.where(
    (ges.SNR > 20) & (ges.REC_WG == 'WG11') & (ges.E_FEH < 0.15) & (ges.E_VRAD < 10.) & (ges.E_TEFF < 100.) & (
            ges.E_LOGG < 0.2))[0]
stellar_data = ges[selection]

# Divide stars up into bins in parameter space
bins = []
# Create metallicity bins
for metallicity_bin in (
        (0, None),
        (-0.5, 0),
        (-1, -0.5),
        (None, -1)
):
    # Create bins by stellar type, based of Teff/logg cuts
    for stellar_type in (
            {"teff_min": 4000, "teff_max": 6000, "logg_min": 3.5},
            {"teff_min": 6000, "logg_min": 3},
            {"name": "giants", "logg_max": 3},
            {"name": "misfits"}
    ):
        bin_constraints = {}
        if metallicity_bin[0] is not None:
            bin_constraints["feh_min"] = metallicity_bin[0]
        if metallicity_bin[1] is not None:
            bin_constraints["feh_max"] = metallicity_bin[1]

        bin_constraints.update(stellar_type)
        bins.append({
            "constraints": bin_constraints,
            "contents": []
        })

# Divide UVES stars in bins
for star in range(len(stellar_data)):
    teff = stellar_data.TEFF[star]
    logg = stellar_data.LOGG[star]
    feh = stellar_data.FEH[star]
    for bin in bins:
        if (
                ("teff_min" not in bin["constraints"] or teff >= bin["constraints"]["teff_min"]) and
                ("teff_max" not in bin["constraints"] or teff < bin["constraints"]["teff_max"]) and
                ("logg_min" not in bin["constraints"] or logg >= bin["constraints"]["logg_min"]) and
                ("logg_max" not in bin["constraints"] or logg < bin["constraints"]["logg_max"]) and
                ("feh_min" not in bin["constraints"] or feh >= bin["constraints"]["feh_min"]) and
                ("feh_max" not in bin["constraints"] or feh < bin["constraints"]["feh_max"])
        ):
            bin["contents"].append(star)
            break

# Create new list of stars producing 300 perturbed versions from each bin
star_list = []
test_stars_per_bin = 300
for bin in bins:
    if bin["contents"]:
        for i in range(test_stars_per_bin):
            random_star = random.choice(bin["contents"])
            test_star = {
                "Teff": stellar_data.TEFF[random_star] + random.gauss(0, 100),
                "logg": stellar_data.LOGG[random_star] + random.gauss(0, 0.1),
                "[Fe/H]": stellar_data.FEH[random_star] + random.gauss(0, 0.1),
                "extra_metadata": {},
                "free_abundances": {},
                "input_data": {}
            }

            free_abundances = test_star["free_abundances"]
            for elements, ionisation_state in ((element_list, 1), (element_list_ionised, 2)):
                for element in elements:
                    if (not synthesizer.args.elements) or (element in synthesizer.args.elements.split(",")):
                        fits_field_name = "{}{}".format(element.upper(), ionisation_state)

                        # Normalise abundance of element to solar
                        abundance = stellar_data[fits_field_name][random_star] - ges[fits_field_name][sun_id]

                        if np.isfinite(abundance):
                            free_abundances[element] = float(abundance) + random.gauss(0, 0.1)
            star_list.append(test_star)

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
