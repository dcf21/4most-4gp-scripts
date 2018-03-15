#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take the [Teff, log_g, Fe/H] parameter values in the MARCs grid of model atmospheres, and synthesize a spectrum at each
point in parameter space. Assume solar abundance ratios for all other elements.
"""

import re
from os import path as os_path
import logging
import glob
from base_synthesizer import Synthesizer

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing MARCS grid of spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="marcs_grid",
                          logger=logger,
                          docstring=__doc__)


def fetch_marcs_grid(marcs_grid_path):
    """
    Get a list of all of the MARCS models we have.

    :return:
        None
    """

    pattern = r"([sp])(\d\d\d\d)_g(....)_m(...)_t(..)_(..)_z(.....)_" \
              r"a(.....)_c(.....)_n(.....)_o(.....)_r(.....)_s(.....).mod"

    marcs_values = {
        "temperature": [],
        "log_g": [],
        "metallicity": []
    }

    marcs_models = glob.glob(os_path.join(marcs_grid_path, "*"))
    for item in marcs_models:

        # Extract model parameters from .mod filename
        filename = os_path.split(item)[1]
        re_test = re.match(pattern, filename)
        assert re_test is not None, "Could not parse MARCS model filename <{}>".format(filename)

        try:
            model = {
                "spherical": re_test.group(1),
                "temperature": float(re_test.group(2)),
                "log_g": float(re_test.group(3)),
                "mass": float(re_test.group(4)),
                "turbulence": float(re_test.group(5)),
                "model_type": re_test.group(6),
                "metallicity": float(re_test.group(7)),
                "a": float(re_test.group(8)),
                "c": float(re_test.group(9)),
                "n": float(re_test.group(10)),
                "o": float(re_test.group(11)),
                "r": float(re_test.group(12)),
                "s": float(re_test.group(13))
            }
        except ValueError:
            logger.error("Could not parse MARCS model filename <{}>".format(filename))
            raise

        # Keep a list of all of the parameter values we've seen
        for parameter, value in model.iteritems():
            if parameter in marcs_values:
                if value not in marcs_values[parameter]:
                    marcs_values[parameter].append(value)

    # Sort model parameter values into order
    for parameter in marcs_values:
        marcs_values[parameter].sort()

    return marcs_values


# Fetch details of the MARCS grid the synthesizer is using
marcs_grid_path = os_path.join(synthesizer.args.binary_path, "fromBengt/marcs_grid")
parameter_values = fetch_marcs_grid(marcs_grid_path=marcs_grid_path)

for key, value in parameter_values.iteritems():
    logger.info("We have {:6d} values for parameter <{}>: {}".format(len(value), key, value))

# Iterate over the spectra we're supposed to be synthesizing
star_list = []
for i1, t_eff in enumerate(parameter_values['temperature']):
    for i2, log_g in enumerate(parameter_values['log_g']):
        for i3, fe_h in enumerate(parameter_values['metallicity']):
            # Create name for star based on its grid position
            star_name = "marcs_{:02d}_{:02d}_{:02d}".format(i1, i2, i3)

            # Add star to the list to be synthesized
            # Apply a small perturbation because the MARCs model interpolator prefers it that way
            star_list.append(
                {'name': star_name,
                 'Teff': min(t_eff + 10, 7990),
                 '[Fe/H]': min(fe_h + 0.01, 0.99),
                 'logg': min(log_g + 0.01, 5.49)
                 })

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
