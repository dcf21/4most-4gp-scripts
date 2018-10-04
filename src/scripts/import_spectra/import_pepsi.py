#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python import_pepsi.py>, but <./import_pepsi.py> will not work.

"""
Take the FITS files containing the PEPSI sample, and import them into a spectrum library. Pass them through 4FS
along the way to sample them onto the 4MOST wavelength raster. We set 4FS to use a very high SNR to avoid adding
much extra noise into them.
"""

import argparse
import glob
import hashlib
import logging
import os
import re
from os import path as os_path

import numpy as np
from astropy.io import fits
from fourgp_degrade import SpectrumResampler
from fourgp_fourfs import FourFS
from fourgp_speclib import SpectrumLibrarySqlite, Spectrum

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../../../..")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library-lrs', default="pepsi_4fs_lrs", dest='library_lrs',
                    help="Spectrum library to insert LRS spectra into.")
parser.add_argument('--library-hrs', default="pepsi_4fs_hrs", dest='library_hrs',
                    help="Spectrum library to insert HRS spectra into.")
parser.add_argument('--library-original', default="pepsi_original", dest='library',
                    help="Spectrum library to insert the original PEPSI spectra into.")
parser.add_argument('--fits-path', default="../../../../pepsi/", dest='fits_path',
                    help="The path to the FITS file to import.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where 4FS package is installed.")
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
args = parser.parse_args()

# Open ASCII table which lists the measured abundances of the PEPSI stars
abundance_data = {}
for ascii_table, split_character in [("2015A&A...582A..49H_table_1.txt", None),
                                     ("2015A&A...582A..49H_table_10.txt", None),
                                     ("benchmark_stars_overview.txt", "\t")
                                     ]:
    ascii_table_filename = os_path.join(args.fits_path, ascii_table)
    column_headings = []
    for line_count, line in enumerate(open(ascii_table_filename)):
        # Ignore blank lines and comment lines
        line = line.strip()
        if (len(line) < 1) or (line[0] == "#"):
            continue

        # First line contains tab-separated column headings
        if line_count == 0:
            column_headings = line.split(split_character)
            continue

        # Subsequent lines contain tab-separated known abundances for objects
        data = line.split(split_character)
        star_name = data[column_headings.index("star")]

        # If we've not seen this star before, create an empty record for it in <abundance_data>
        if star_name not in abundance_data:
            abundance_data[star_name] = {}

        # Transfer data from table into <abundance_data>
        for column_number, column_name in enumerate(column_headings):
            column_value = str(data[column_number])
            # Ignore NaNs
            if column_value in ("NaN", "-"):
                continue

            # See if column contains numeric data
            try:
                column_value = float(column_value)
            except ValueError:
                pass

            # Add data to <abundance_data>
            abundance_data[star_name][column_name] = column_value

# Set path to workspace where we create libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")
os.system("mkdir -p {}".format(workspace))

# Create new SpectrumLibrary(s) to hold the output from 4FS
output_libraries = {}

for mode, output_library in (("original", args.library),
                             ("LRS", args.library_lrs),
                             ("HRS", args.library_hrs)):
    library_name = re.sub("/", "_", output_library)
    library_path = os_path.join(workspace, library_name)
    output_libraries[mode] = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Instantiate 4FS wrapper
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
    magnitude=13,
    snr_list=[250]
)

# Open fits spectrum
for item in glob.glob(os_path.join(args.fits_path, "*.all6")):
    filename = os_path.split(item)[1]

    # Open FITS file
    f = fits.open(item)

    # Extract headers and import them as metadata in SpectrumLibrary
    headers = f[0].header

    # Extract name of object
    star_name = str(headers['OBJECT'].strip())

    header_dictionary = {'Starname': star_name,
                         'original_filename': filename
                         }

    # Truncate each FITS header to only the first line. Also, omit various fields, otherwise we get hundreds of fields
    # we don't need.
    for key in headers:
        if ((not key.startswith("BCOL")) and (not key.startswith("GAIN")) and
                (not key.startswith("IMASEC")) and (not key.startswith("RON"))):
            header_dictionary[key] = str(headers[key]).strip().split("\n")[0]

    # Extract radial velocity of object -- units m/s, with receding velocity being positive
    radial_velocity = float(header_dictionary['RADVEL'])

    # Remove spaces to match the names in the ASCII table of abundances
    star_name = re.sub(" ", "", star_name)

    # Extract list of metadata from <abundance_data>
    if star_name not in abundance_data:
        print("Warning: star <{}> not found in ASCII table".format(star_name))
    else:
        header_dictionary.update(abundance_data[star_name])

    # 1. Extract continuum-normalised spectrum from FITS file
    data = f[1].data

    wavelengths = data['Arg']
    flux = data['Fun']
    flux_errors = data['Var']

    pepsi_spectrum = Spectrum(wavelengths=wavelengths,
                              values=flux,
                              value_errors=flux_errors,
                              metadata=header_dictionary)

    # Create a unique ID for this PEPSI spectrum
    unique_id = hashlib.md5(os.urandom(32)).hexdigest()[:16]
    header_dictionary["uid"] = unique_id

    output_libraries['original'].insert(spectra=pepsi_spectrum,
                                        filenames=star_name,
                                        metadata_list=header_dictionary
                                        )

    # 2. Correct radial velocity
    # pepsi_spectrum_rest_frame = pepsi_spectrum.correct_radial_velocity(radial_velocity)

    # Don't need to do the above, because the spectra are already RV corrected
    pepsi_spectrum_rest_frame = pepsi_spectrum

    # 3. Resample spectrum onto a wavelength raster with fixed stride, as this is what 4FS requires
    resampler = SpectrumResampler(input_spectrum=pepsi_spectrum_rest_frame)
    lambda_min = wavelengths[0] + 10
    lambda_max = wavelengths[-1] - 10
    lambda_delta = 0.05
    lambda_steps = (lambda_max - lambda_min) / lambda_delta
    pepsi_spectrum_resampled = resampler.onto_raster(output_raster=np.linspace(start=lambda_min,
                                                                               stop=lambda_max,
                                                                               num=lambda_steps
                                                                               ))

    # Process spectra through 4FS
    degraded_spectra = etc_wrapper.process_spectra(
        spectra_list=((pepsi_spectrum_resampled.copy(),
                       pepsi_spectrum_resampled.copy()),),
        resolution=(lambda_max + lambda_min) / 2 / lambda_delta
    )

    # Import degraded spectra into output spectrum library

    # Loop over LRS and HRS
    for mode in degraded_spectra:
        # Loop over the spectra we simulated (there was only one!)
        for index in degraded_spectra[mode]:
            # Loop over the single SNR that we simulated
            for snr in degraded_spectra[mode][index]:
                # Create a unique ID for this mock observation
                unique_id = hashlib.md5(os.urandom(32)).hexdigest()[:16]
                header_dictionary["uid"] = unique_id
                # Import the flux- and continuum-normalised spectra separately, but give them the same ID
                for spectrum_type in degraded_spectra[mode][index][snr]:
                    output_libraries[mode].insert(spectra=degraded_spectra[mode][index][snr][spectrum_type],
                                                  filenames=star_name,
                                                  metadata_list=header_dictionary
                                                  )

# Clean up 4FS
etc_wrapper.close()
