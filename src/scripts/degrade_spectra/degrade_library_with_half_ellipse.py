#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python degrade_library_with_gaussian.py>, but <./degrade_library_with_gaussian.py> will not work.

"""
Take a library of spectra, and convolve each spectrum with a half ellipse.
"""

import argparse
import os
from os import path as os_path
import time
import re
import logging
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__.strip())
parser.add_argument('--input-library',
                    required=False,
                    default="galah_test_sample_4fs_hrs_50only",
                    dest="input_library",
                    help="The name of the spectrum library we are to read input spectra from. A subset of the stars "
                         "in the input library may optionally be selected by suffixing its name with a comma-separated "
                         "list of constraints in [] brackets. Use the syntax my_library[Teff=3000] to demand equality, "
                         "or [0<[Fe/H]<0.2] to specify a range. We do not currently support other operators like "
                         "[Teff>5000], but such ranges are easy to recast is a range, e.g. [5000<Teff<9999].")
parser.add_argument('--output-library',
                    required=False,
                    default="galah_test_sample_4fs_hrs_he_50only",
                    dest="output_library",
                    help="The name of the spectrum library we are to feed the convolved spectra into.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--width',
                    required=False,
                    default="1.7",
                    dest="width",
                    help="The width of the half-ellipse convolution function.")
parser.add_argument('--create',
                    action='store_true',
                    dest="create",
                    help="Create a clean spectrum library to feed output spectra into. Will throw an error if "
                         "a spectrum library already exists with the same name.")
parser.add_argument('--no-create',
                    action='store_false',
                    dest="create",
                    help="Do not create a clean spectrum library to feed output spectra into.")
parser.set_defaults(create=True)
parser.add_argument('--log-file',
                    required=False,
                    default="/tmp/half_ellipse_convolution_{}.log".format(pid),
                    dest="log_to",
                    help="Specify a log file where we log our progress.")
args = parser.parse_args()

logger.info("Adding half-ellipse convolution to spectra from <{}>, going into <{}>".format(args.input_library,
                                                                                           args.output_library))

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")
os.system("mkdir -p {}".format(workspace))

# Open input SpectrumLibrary, and search for flux normalised spectra meeting our filtering constraints
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=args.input_library,
                                                workspace=workspace,
                                                extra_constraints={}
                                                )

# Get a list of the spectrum IDs which we were returned
input_library, input_spectra_ids, input_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

# Create new spectrum library for output
library_name = re.sub("/", "_", args.output_library)
library_path = os_path.join(workspace, library_name)
output_library = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Parse the half-ellipse width that the user specified on the command line
half_ellipse_width = float(args.width)

# Create half-ellipse convolution function
half_ellipse_raster = np.arange(-3, 3.1)
half_ellipse = np.sqrt(np.maximum(0, 1 - half_ellipse_raster ** 2 / half_ellipse_width ** 2))

# Start making a log file
with open(args.log_to, "w") as result_log:
    # Loop over spectra to process
    for input_spectrum_id in input_spectra_ids:
        logger.info("Working on <{}>".format(input_spectrum_id['filename']))
        # Open Spectrum data from disk
        input_spectrum_array = input_library.open(ids=input_spectrum_id['specId'])

        # Turn SpectrumArray object into a Spectrum object
        input_spectrum = input_spectrum_array.extract_item(0)

        # Look up the unique ID of the star we've just loaded
        # Newer spectrum libraries have a uid field which is guaranteed unique; for older spectrum libraries use
        # Starname instead.

        # Work out which field we're using (uid or Starname)
        spectrum_matching_field = 'uid' if 'uid' in input_spectrum.metadata else 'Starname'

        # Look up the unique ID of this object
        object_name = input_spectrum.metadata[spectrum_matching_field]

        # Write log message
        result_log.write("\n[{}] {}... ".format(time.asctime(), object_name))
        result_log.flush()

        # Convolve spectrum
        flux_data = input_spectrum.values
        flux_data_convolved = np.convolve(a=flux_data, v=half_ellipse, mode='same')

        flux_errors = input_spectrum.value_errors
        flux_errors_convolved = np.convolve(a=flux_errors, v=half_ellipse, mode='same')

        output_spectrum = Spectrum(wavelengths=input_spectrum.wavelengths,
                                   values=flux_data_convolved,
                                   value_errors=flux_errors_convolved,
                                   metadata=input_spectrum.metadata
                                   )

        # Import degraded spectra into output spectrum library
        output_library.insert(spectra=output_spectrum,
                              filenames=input_spectrum_id['filename'],
                              metadata_list={"half_ellipse_width": half_ellipse_width})
