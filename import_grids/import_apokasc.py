#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take the APOKASC training set and test sets, and turn them into SpectrumLibraries for use in 4MOST 4GP
"""

import os
import re
import glob
from os import path as os_path
import logging
from astropy.table import Table

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Importing APOKASC grid of spectra")

# Path to where we find Keith Hawkins's <4MOST_testspectra>
our_path = os_path.split(os_path.abspath(__file__))[0]
test_spectra_path = os_path.join(our_path, "..", "..", "4MOST_testspectra")

# Set path to workspace where we create libraries of spectra
workspace = os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))


# Convenience function, coz it would've been too helpful for astropy to actually provide dictionary access to rows
def astropy_row_to_dict(x):
    return dict([(i, x[i]) for i in x.columns])


# Table supplies list of stars in the APOKASC training set, giving the stellar labels for each star in the training set
training_set = Table.read(os_path.join(test_spectra_path, "trainingset_param.tab"), format="ascii")

# Table supplies list of expected stellar labels for each star in the test dataset
expected_test_output = Table.read(os_path.join(test_spectra_path, "testset_param.tab"), format="ascii")
expected_test_output_dict = dict([(star['Starname'], astropy_row_to_dict(star)) for star in expected_test_output])

# Import high-resolution and low-resolution training sets into SpectrumLibraries
for training_set_dir in ["APOKASC_trainingset/HRS", "APOKASC_trainingset/LRS"]:

    # Turn training set into a SpectrumLibrary with path specified above
    library_name = re.sub("/", "_", training_set_dir)
    library_path = os_path.join(workspace, library_name)
    library = SpectrumLibrarySqlite(path=library_path, create=True)

    # Import each star in turn
    for star in training_set:
        filepath = os_path.join(test_spectra_path, training_set_dir, "{}_SNR250.txt".format(star["Starname"]))
        filename = os_path.split(filepath)[1]
        metadata = astropy_row_to_dict(star)
        spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, binary=False)
        library.insert(spectra=spectrum, filenames=filename)

# Import high-resolution and low-resolution test sets into SpectrumLibraries
for test_set_dir in ["testset/HRS", "testset/LRS"]:

    # Turn training set into a SpectrumLibrary with path specified above
    library_name = re.sub("/", "_", test_set_dir)
    library_path = os_path.join(workspace, library_name)
    library = SpectrumLibrarySqlite(path=library_path, create=True)

    # Import each star in turn
    test_set = glob.glob(os_path.join(test_spectra_path, test_set_dir, "star*_SNR*.txt"))
    for filepath in test_set:
        # Identify which star it is, and its SNR
        basename = os_path.basename(filepath)
        star_number = int(basename.split("_")[0].lstrip("star"))
        snr = int(basename.split("_")[1].split(".")[0].lstrip("SNR"))
        star_name = "star{:04d}".format(star_number)

        metadata = expected_test_output_dict[star_name]
        metadata.update({"star": star_number, "snr": snr})

        # Read star from text file and import it into our SpectrumLibrary
        spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, binary=False)
        filename = os_path.split(filepath)[1]
        library.insert(spectra=spectrum, filenames=filename)
