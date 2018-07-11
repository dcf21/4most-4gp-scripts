#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python import_pepsi.py>, but <./import_pepsi.py> will not work.

"""
Take the FITS files containing the PEPSI sample, and import them into a spectrum library. Pass them through 4FS
along the way to sample them onto the 4MOST wavelength raster.
"""

import argparse
import os
from os import path as os_path
import glob
import hashlib
import logging
import re
from astropy.io import fits

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_fourfs import FourFS

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../..")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library-lrs', default="pepsi_4fs_lrs", dest='library_lrs',
                    help="Spectrum library to insert LRS spectrum into.")
parser.add_argument('--library-hrs', default="pepsi_4fs_hrs", dest='library_hrs',
                    help="Spectrum library to insert HRS spectrum into.")
parser.add_argument('--fits-path', default="../../pepsi/", dest='fits_path',
                    help="The path to the FITS file to import.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where 4FS package is installed.")
parser.add_argument('--create',
                    required=False,
                    action='store_true',
                    dest="create",
                    help="Create a clean SpectrumLibrary to feed synthesized spectra into")
parser.add_argument('--no-create',
                    required=False,
                    action='store_false',
                    dest="create",
                    help="Do not create a clean SpectrumLibrary to feed synthesized spectra into")
parser.set_defaults(create=True)
args = parser.parse_args()

# Set path to workspace where we create libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")
os.system("mkdir -p {}".format(workspace))

# Create new LRS SpectrumLibrary
output_libraries = {}
for mode, output_library in (("LRS", args.library_lrs), ("HRS", args.library_hrs)):
    library_name = re.sub("/", "_", output_library)
    library_path = os_path.join(workspace, library_name)
    output_libraries[mode] = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Instantiate 4FS wrapper
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
    magnitude=13,
    snr_list=[1000]
)

# Open fits spectrum
for item in glob.glob(os_path.join(args.fits_path, "*.all6")):
    star_name = os_path.split(item)[1]

    # Extract continuum normalised spectrum from FITS file
    f = fits.open(item)
    data = f[1].data

    wavelengths = data['Arg']
    flux = data['Fun']
    flux_errors = data['Var']

    pepsi_spectrum = Spectrum(wavelengths=wavelengths,
                              values=flux,
                              value_errors=flux_errors,
                              metadata={'Starname': star_name})

    # Process spectra through 4FS
    degraded_spectra = etc_wrapper.process_spectra(
        spectra_list=((pepsi_spectrum, pepsi_spectrum),)
    )

    # Import degraded spectra into output spectrum library
    for mode in degraded_spectra:
        for index in degraded_spectra[mode]:
            for snr in degraded_spectra[mode][index]:
                unique_id = hashlib.md5(os.urandom(32).encode("hex")).hexdigest()[:16]
                for spectrum_type in degraded_spectra[mode][index][snr]:
                    output_libraries[mode].insert(spectra=degraded_spectra[mode][index][snr][spectrum_type],
                                                  filenames=star_name,
                                                  metadata_list={"uid": unique_id,
                                                                 "fits_filename": star_name}
                                                  )
