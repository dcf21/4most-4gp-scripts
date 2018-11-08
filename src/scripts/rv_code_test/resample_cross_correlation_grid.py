#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python resample_cross_correlation_grid.py>, but <./resample_cross_correlation_grid.py> will not work.

"""
Take some high resolution spectra that we're going to use as templates for cross correlation to determine RVs, and
use 4FS to down-sample them to the resolution of 4MOST observations for use in cross correlation.
"""

from os import path as os_path
import logging

from fourgp_rv.templates_resample import command_line_interface, resample_templates

# Set up logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info("Resampling cross-correlation templates")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../../../..")
args = command_line_interface(root_path=root_path)
args.our_path = our_path

# Resample templates
resample_templates(args=args,
                   logger=logger)
