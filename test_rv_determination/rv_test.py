#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take the APOKASC training set and test sets, apply random radial velocities to the spectra, and see how well fourgp_rv
can determine what radial velocity we applied.
"""

from os import path as os_path
import logging
import time
import numpy as np

from fourgp_rv import RvInstance

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info("Testing fourgp_rv")

# Set path to workspace where we expect to find a library of template spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "workspace")
target_library_name = "brani_rv_grid"
library_path = os_path.join(workspace, target_library_name)

# Instantiate the RV code
time_start = time.time()
rv_code = RvInstance.from_spectrum_library_sqlite(library_path=library_path)
time_end = time.time()
logger.info("Set up time was {:.2f} sec".format(time_end-time_start))
