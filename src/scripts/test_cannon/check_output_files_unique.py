#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python check_output_files_unique.py>, but <./check_output_files_unique.py> will not work.

"""
Check that the bash scripts in <examples> are not going to do multiple runs of the Cannon and save the output to the
same destination. I'm really bad at forgetting to change the destination filename when I create new tests, so this is a
useful check...
"""

import argparse
import glob
import logging
import re

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__.strip())
parser.add_argument('--input-file', action="append", dest='input_files', default="examples/*.sh",
                    help="Bash script to check for clashing output destinations.")
args = parser.parse_args()

if not isinstance(args.input_files, (tuple, list)):
    args.input_files = [args.input_files]

logger.info("Checking uniqueness of output files in {}".format(args.input_files))

destinations = {}

for input_wildcard in args.input_files:
    for script in glob.glob(input_wildcard):
        for line_number, line in enumerate(open(script, "rt")):
            line = line.strip()
            test = re.match("--output-file \"(.*)\"", line)
            if test is not None:
                destination = test.group(1)
                reference_new = (script, line_number)
                if destination in destinations:
                    reference_old = destinations[destination]
                    logger.warning("* Clash for output <{}>".format(destination))
                    logger.warning("  between {0}:{1}".format(*reference_old))
                    logger.warning("  and     {0}:{1}".format(*reference_new))
                else:
                    destinations[destination] = reference_new
