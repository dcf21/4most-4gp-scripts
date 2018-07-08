#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_saga.py>, but <./synthesize_saga.py> will not work.

"""
Take parameters of the SAGA survey, and synthesize spectra using TurboSpectrum.

Parameters downloaded from here: http://sagadatabase.jp/?page_id=10
"""

import re
import numpy as np
import logging
from lib.base_synthesizer import Synthesizer

# List of elements whose abundances we pass to TurboSpectrum
# Elements with neutral abundances, e.g. LI1
element_list = (
    "Li", "B", "Be", "C", "N", "O", "Na", "Mg", "Al", "Si", "S", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Ni",
    "Co", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Mo", "Ru", "Rh", "Pd", "Ag",
    "Cd", "Sn", "Te", "Ba", "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er",
    "Tm", "Yb", "Lu", "Hf", "W", "Os", "Ir", "Pt", "Au", "Hg", "Pb", "Bi", "Th", "U")

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing SAGA spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="saga_sample",
                          logger=logger,
                          docstring=__doc__)


def valid_float(n):
    try:
        test = re.match("<?(.*)+-.*", n)
        if test is not None:
            n = test.group(1)
        n = float(n)
    except ValueError:
        return None
    except TypeError:
        return None
    return n


# Open list of stars
f = open("../../downloads/saga_survey.txt").readlines()
stars = []
columns = f[0].split("\t")

for line in f[1:]:
    star = dict(zip(columns, line.split("\t")))
    valid_star = True
    print len(columns), len(line.split("\t"))
    for essential_item in ['Teff', 'log g', 'Fe']:
        if essential_item not in star:
            valid_star = False
        elif valid_float(star[essential_item]) is None:
            valid_star = False
    if not valid_star:
        continue
    stars.append(star)

# Create a list of the stars we're going to synthesize
star_list = []
for star in stars:
    item = {'name': star['Object'],
            "Teff": valid_float(star['Teff']),
            "[Fe/H]": valid_float(star['Fe']),
            "logg": valid_float(star['log g'])
            }

    # Pass list of the abundances of individual elements to TurboSpectrum
    free_abundances = {}
    for element in element_list:
        if (not synthesizer.args.elements) or (element in synthesizer.args.elements.split(",")):
            for ionisation_state in [" II", " I", ""]:
                field_name = "{}{}".format(element, ionisation_state)

                if field_name in star:
                    abundance = valid_float(star[field_name])

                    if (abundance is not None) and np.isfinite(abundance):
                        free_abundances[element] = abundance
    item['free_abundances'] = free_abundances
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
