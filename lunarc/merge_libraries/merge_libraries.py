#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

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
args = parser.parse_args()

logger.info("Running library merger on spectra with arguments <{}>".format(args.input_library))

# Set path to workspace where we create libraries of spectra
workspace = os_path.join(our_path, "..", "workspace")

input_libraries = glob.glob("{}/{}_*".format(workspace,args.input_library))
input_libraries.sort()

command_line = "cd ../rearrange_libraries ; python rearrange.py "

for item in input_libraries:
    command_line += " --input-library {}".format(os.path.split(item)[1])

command_line += " --output-library {}".format(args.input_library)

print command_line
os.system(command_line)

