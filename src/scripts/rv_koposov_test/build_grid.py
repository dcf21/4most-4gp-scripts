#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python convolve_library.py>, but <./convolve_library.py> will not work.

"""

Build the grid of template spectra required by Sergey Koposov's RV code.

This code takes the Phoenix grid of high resolution template spectra, and down-samples them to the same resolution
as each arm of 4MOST.

Before you start, the Phoenix grid needs to be downloaded from
<ftp://phoenix.astro.physik.uni-goettingen.de/v2.0/HiResFITS/>.

"""

import argparse
import os
import sys
from os import path as os_path
import logging
import numpy as np

import rvspecfit.read_grid
import rvspecfit.make_interpol
import rvspecfit.make_nd
import rvspecfit.make_ccf

from fourgp_degrade import SpectrumProperties

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__.strip())
parser.add_argument('--input-phoenix',
                    required=False,
                    default="/mnt/data/phoenix/phoenix.astro.physik.uni-goettingen.de/v2.0/HiResFITS/",
                    dest="input_phoenix",
                    help="The path to the high resolution Phoenix grid, that you should download from "
                         "<ftp://phoenix.astro.physik.uni-goettingen.de/v2.0/HiResFITS/>.")
parser.add_argument('--output-directory',
                    required=False,
                    default="/mnt/data/phoenix/4most_templates",
                    dest="output_directory",
                    help="The path where we should store the resampled template spectra, together with an SQLite3 "
                         "database listing the templates we have.")
parser.add_argument('--log-file',
                    required=False,
                    default="/tmp/build_koposov_grid_{}.log".format(pid),
                    dest="log_to",
                    help="Specify a log file where we log our progress.")
args = parser.parse_args()

# Start creating log file
logging.basicConfig(filename=args.log_to, filemode='w',
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info("Building phoenix template spectra from <{}>, going into <{}>".format(args.input_phoenix,
                                                                                  args.output_directory))

# Identifying 4MOST wavelength arms
spectrograph_modes = ('hrs', 'lrs')
spectrograph_arms = ('blu', 'grn', 'red')
all_wavelength_arms = {}

for mode in spectrograph_modes:
    raster = np.loadtxt(os_path.join(our_path, "../degrade_spectra/raster_{mode}.txt".format(mode=mode))).transpose()[0]
    wavelength_arms = SpectrumProperties(raster).wavelength_arms()

    for arm_name, arm in zip(spectrograph_arms, wavelength_arms["wavelength_arms"]):
        arm_raster, mean_pixel_width = arm
        name = "{}_{}".format(mode, arm_name)
        all_wavelength_arms[name] = {
            "lambda_min": arm_raster[0],
            "lambda_max": arm_raster[-1],
            "lambda_step": mean_pixel_width
        }

# Print information about the wavelength arms we have identified
logger.info("Identified 4MOST wavelength arms as follows:")
for arm_name in sorted(all_wavelength_arms.keys()):
    arm = all_wavelength_arms[arm_name]
    logger.info("{0:10s}: min {1:10.1f} max {2:10.1f} step {3:10.5f}".format(arm_name,
                                                                             arm["lambda_min"],
                                                                             arm["lambda_max"],
                                                                             arm["lambda_step"]))

# Create output directory
if os_path.exists(args.output_directory):
    logger.error("Directory <{}> already exists. Aborting to avoid overwriting existing data.".
                 format(args.output_directory))
    sys.exit(1)

os.system("mkdir -p {}".format(args.output_directory))

# Build SQLite3 database of template spectra
logger.info("Calling <rvspecfit.read_grid.makedb>")
db_file = os_path.join(args.output_directory, "files.db")
phoenix_dir = os_path.join(args.input_phoenix, "PHOENIX-ACES-AGSS-COND-2011/")
phoenix_raster = os_path.join(args.input_phoenix, "WAVE_PHOENIX-ACES-AGSS-COND-2011.fits")
rvspecfit.read_grid.makedb(prefix=phoenix_dir,
                           dbfile=db_file
                           )

# Now resample the Phoenix spectra onto all the wavelength arms we're going to need
for arm_name in sorted(all_wavelength_arms.keys()):
    logger.info("Calling <rvspecfit.make_interpol.process_all> for arm <{}>".format(arm_name))
    arm = all_wavelength_arms[arm_name]
    output_directory = os_path.join(args.output_directory, arm_name)

    rvspecfit.make_interpol.process_all(setupInfo=(arm_name,
                                                   arm["lambda_min"],
                                                   arm["lambda_max"],
                                                   (arm["lambda_max"] + arm["lambda_min"]) / 2 / arm["lambda_step"],
                                                   arm["lambda_step"],
                                                   False),
                                        dbfile=db_file,
                                        oprefix=output_directory,
                                        prefix=phoenix_dir,
                                        wavefile=phoenix_raster,
                                        air=True,
                                        resolution0=100000,
                                        fixed_fwhm=False
                                        )

# Create the triangulation tables
for arm_name in sorted(all_wavelength_arms.keys()):
    logger.info("Calling <rvspecfit.make_interpol.process_all> for arm <{}>".format(arm_name))
    arm = all_wavelength_arms[arm_name]
    output_directory = os_path.join(args.output_directory, arm_name)

    rvspecfit.make_nd.execute(spec_setup=arm_name,
                              prefix=output_directory
                              )

# Create Fourier transforms of the templates
for arm_name in sorted(all_wavelength_arms.keys()):
    logger.info("Calling <rvspecfit.make_ccf> for arm <{}>".format(arm_name))
    arm = all_wavelength_arms[arm_name]
    output_directory = os_path.join(args.output_directory, arm_name)

    # Settings I copied from the WEAVE configuation
    v_sin_i_values = (0, 300)
    every = 30

    n_points = (arm["lambda_max"] - arm["lambda_min"]) / arm["lambda_step"]
    ccf_conf = rvspecfit.make_ccf.CCFConfig(logl0=np.log(arm["lambda_min"]),
                                            logl1=np.log(arm["lambda_max"]),
                                            npoints=n_points
                                            )

    rvspecfit.make_ccf.ccf_executor(spec_setup=arm_name,
                                    ccfconf=ccf_conf,
                                    prefix=output_directory,
                                    oprefix=output_directory,
                                    every=30,
                                    vsinis=v_sin_i_values)

# Finished
logger.info("Work complete")
