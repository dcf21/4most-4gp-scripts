#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take spectrum library, and export the spectra in it in ASCII format.
"""

import os
from os import path as os_path
import argparse
import re
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Spectrum library we should export, with additional constraints if wanted.")
parser.add_argument('--output-stub', default="/tmp/my_spectra", dest='output_stub',
                    help="Directory to write output to.")
args = parser.parse_args()


# Helper for opening input SpectrumLibrary(s)
def open_input_libraries(library_spec, extra_constraints):
    test = re.match("([^\[]*)\[(.*)\]$", library_spec)
    constraints = {}
    if test is None:
        library_name = library_spec
    else:
        library_name = test.group(1)
        for constraint in test.group(2).split(","):
            words_1 = constraint.split("=")
            words_2 = constraint.split("<")
            if len(words_1) == 2:
                constraint_name = words_1[0]
                try:
                    constraint_value = float(words_1[1])
                except ValueError:
                    constraint_value = words_1[1]
                constraints[constraint_name] = constraint_value
            elif len(words_2) == 3:
                constraint_name = words_2[1]
                try:
                    constraint_value_a = float(words_2[0])
                    constraint_value_b = float(words_2[2])
                except ValueError:
                    constraint_value_a = words_2[0]
                    constraint_value_b = words_2[2]
                constraints[constraint_name] = (constraint_value_a, constraint_value_b)
            else:
                assert False, "Could not parse constraint <{}>".format(constraint)
    constraints.update(extra_constraints)
    constraints["continuum_normalised"] = 1  # All input spectra must be continuum normalised
    library_path = os_path.join(workspace, library_name)
    input_library = SpectrumLibrarySqlite(path=library_path, create=False)
    library_items = input_library.search(**constraints)
    return {
        "library": input_library,
        "items": library_items
    }


# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "workspace")

# Open spectrum library we're going to plot
input_library_info = open_input_libraries(args.library, {})
input_library, library_items = [input_library_info[i] for i in ("library", "items")]
library_ids = [i["specId"] for i in library_items]
library_spectra = input_library.open(ids=library_ids)

# Create output directory
os.system("mkdir -p {}".format(args.output_stub))

# Write out spectra one by one
for i in range(len(library_spectra)):
    metadata = library_spectra.get_metadata(i)

    if "Starname" not in metadata:
        metadata["Starname"] = "untitled"
    if "SNR" not in metadata:
        metadata["SNR"] = 0
    if "e_bv" not in metadata:
        metadata["e_bv"] = 0

    spectrum = library_spectra.extract_item(i)
    filename_stub = os_path.join(args.output_stub, "{0}_{1:06.4f}_{2:06.1f}".format(metadata["Starname"],
                                                                                    metadata["e_bv"],
                                                                                    metadata["SNR"]))

    # Write metadata
    with open("{}.txt".format(filename_stub), "w") as f:
        for key in sorted(metadata.keys()):
            f.write("{0:12s}: {1}\n".format(key, metadata[key]))

    # Write spectrum
    with open("{}.spec".format(filename_stub), "w") as f:
        np.savetxt(f, np.asarray(zip(spectrum.wavelengths, spectrum.values, spectrum.value_errors)))
