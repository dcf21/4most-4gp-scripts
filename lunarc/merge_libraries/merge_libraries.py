#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python merge_libraries.py>, but <./merge_libraries.py> will not work.

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
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-library',
                    required=True,
                    dest="input_library",
                    help="Specify the name of the SpectrumLibrary we are to read input spectra from.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
args = parser.parse_args()

logger.info("Running library merger on spectra with arguments <{}>".format(args.input_library))

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "..", "workspace")

input_libraries = glob.glob("{}/{}_*".format(workspace,args.input_library))
input_libraries.sort()

command_line = "cd ../../rearrange_libraries ; python rearrange.py --workspace \"{}\" ".format(args.workspace)

for item in input_libraries:
    command_line += " --input-library {}".format(os.path.split(item)[1])

command_line += " --output-library {}".format(args.input_library)

print command_line
os.system(command_line)

