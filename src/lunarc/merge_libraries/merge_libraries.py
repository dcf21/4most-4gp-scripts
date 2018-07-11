#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python merge_libraries.py>, but <./merge_libraries.py> will not work.

"""

This script takes the contents of a load of spectrum libraries, and merges them all into one. This is commonly used
immediately after synthesising spectra on lunarc -- since it is generally necessary to get each core to save its output
into a separate spectrum library to avoid database corruption.

You specify an input library pattern, e.g. "demo_stars". We then look for all spectrum libraries whose name starts
"demo_stars_*", and we merge the contents of all of these into one library called simply "demo_stars".

"""

# Some example usages:

# python merge_libraries.py --input-library demo_stars
# python merge_libraries.py --input-library turbospec_ahm2017_perturbed
# python merge_libraries.py --input-library marcs_stars
# python merge_libraries.py --input-library turbospec_marcs_grid
# python merge_libraries.py --input-library turbospec_ges_dwarfs_perturbed

import argparse
import os
from os import path as os_path
import glob
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-library',
                    required=True,
                    dest="input_library",
                    help="Specify the beginning of the name of the spectrum libraries we are to read input spectra "
                         "from. If you specify <demo_stars>, we will merge all spectrum libraries whose names start "
                         "<demo_stars_*> into a single spectrum library called <demo_stars>.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
args = parser.parse_args()

logger.info("Running library merger on spectra with arguments <{}>".format(args.input_library))

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

input_libraries = glob.glob("{}/{}_*".format(workspace, args.input_library))
input_libraries.sort()

command_line = "cd ../../../src/scripts/rearrange_libraries/ ; python rearrange.py --workspace \"{}\" ". \
    format(args.workspace)

for item in input_libraries:
    command_line += " --input-library {}".format(os.path.split(item)[1])

command_line += " --output-library {}".format(args.input_library)

# Show the user the python command we're about to run
print command_line

# Do it!
os.system(command_line)
