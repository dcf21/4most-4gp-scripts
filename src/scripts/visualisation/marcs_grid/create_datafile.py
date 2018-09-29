#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python create_datafile.py>, but <./create_datafile.py> will not work.

"""
Create a data file listing all of the MARCS models we have in a particular grid, which can be plotted using a tool
such as gnuplot or pyxplot.
"""

import argparse
import glob
import logging
import re
from os import path as os_path

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Creating datafile listing all the MARCS models in a grid")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output_file', required=False, default="/tmp/marcs_grid.dat", dest="output")
parser.add_argument('--grid_path', required=False, default="/home/dcf21/iwg7_pipeline/fromBengt/marcs_grid",
                    dest="grid_path")
args = parser.parse_args()


def fetch_marcs_grid(input_path, output_filename):
    """
    Get a list of all of the MARCS models we have.

    :return:
        None
    """

    pattern = r"([sp])(\d\d\d\d)_g(....)_m(...)_t(..)_(..)_z(.....)_" \
              r"a(.....)_c(.....)_n(.....)_o(.....)_r(.....)_s(.....).mod"

    marcs_values = {
        "spherical": [], "temperature": [], "log_g": [], "mass": [], "turbulence": [], "model_type": [],
        "metallicity": [], "a": [], "c": [], "n": [], "o": [], "r": [], "s": []
    }

    marcs_value_keys = list(marcs_values.keys())
    marcs_value_keys.sort()

    marcs_models = glob.glob(os_path.join(input_path, "*"))

    with open(output_filename, "w") as output:

        # Write headers at top of output data
        output.write("# ")
        for parameter in marcs_value_keys:
            output.write("{:12s} ".format(parameter))
        output.write("\n")

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

            # Write line of output data
            for parameter in marcs_value_keys:
                output.write("{:12s} ".format(str(model[parameter])))
            output.write("\n")


fetch_marcs_grid(input_path=args.grid_path, output_filename=args.output)
