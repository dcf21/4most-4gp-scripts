#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python filter_cannon_output.py>, but <./filter_cannon_output.py> will not work.

"""
Take an output JSON file from running the Cannon, and filter the stars within it based on metadata constraints. The
new list of stars is written out as a JSON data file in the same format as the original.
"""

import argparse
from os import path as os_path
import re
import logging
import json
import time
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import CannonInstance

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-file', required=True, dest='input_file',
                    help="JSON data file to read input from.")
parser.add_argument('--output-file', required=True, dest='output_file',
                    help="JSON data file to write output to.")
parser.add_argument('--criteria', required=True, dest='criteria',
                    help="Selection criteria to use when picking stars. Either use format 'Teff=6000' or "
                         "'5000<Teff<6000'.")
parser.set_defaults(multithread=True)
args = parser.parse_args()

logger.info("Testing Cannon filter <{}> <{}> <{}>".format(args.input_file,
                                                          args.output_file,
                                                          args.criteria))

# Read list of filter constraints
constraints = {}
constraints_text = []

for filter in args.criteria.split(","):
    words_1 = filter.split("=")
    words_2 = filter.split("<")
    if len(words_1) == 2:
        constraint_name = words_1[0]
        try:
            constraint_value = float(words_1[1])
        except ValueError:
            constraint_value = words_1[1]
        constraints[constraint_name] = constraint_value
        constraints_text.append("{}$=${}".format(constraint_name, constraint_value))
    elif len(words_2) == 3:
        constraint_name = words_2[1]
        try:
            constraint_value_a = float(words_2[0])
            constraint_value_b = float(words_2[2])
        except ValueError:
            constraint_value_a = words_2[0]
            constraint_value_b = words_2[2]
        constraints[constraint_name] = (constraint_value_a, constraint_value_b)
        constraints_text.append("{}$<${}$<${}".format(constraint_value_a, constraint_name, constraint_value_b))
    else:
        assert False, "Could not parse constraint <{}>".format(filter)

# Read Cannon input file
cannon_json = json.loads(open(args.input_file + ".json").read())

# Filter list of stars
filtered_stars = []
for star in cannon_json["stars"]:
    reject = False
    for constraint_name, constraint_value in constraints.iteritems():
        # We filter stars based on the target values used to synthesise the spectra, not the Cannon output
        target_value_key = "target_{}".format(constraint_name)
        # If this parameter is not set on this star, we exclude it
        if (target_value_key not in star) or (star[target_value_key] is None):
            reject = True
        # If parameter constraint is a tuple, we have lower and upper bounds on acceptable values
        elif isinstance(constraint_value, (list, tuple)):
            if not constraint_value[0] < star[target_value_key] < constraint_value[1]:
                reject = True
        # If we have a single constraint value, we must match it
        else:
            if not star[target_value_key] == constraint_value:
                reject = True
    # Include star in output list only if we've not rejected it
    if not reject:
        filtered_stars.append(star)

# Add a suffix to the description of this Cannon run to say we've filtered it
cannon_json["description"] += " -- {}.".format("; ".join(constraints_text))

# Replace original list of stars with filtered list
cannon_json["stars"] = filtered_stars

# Write results to JSON file
with open(args.output_file + ".json", "w") as f:
    f.write(json.dumps(cannon_json))
