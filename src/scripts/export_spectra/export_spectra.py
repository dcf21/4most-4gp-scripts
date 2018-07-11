#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python export_spectra.py>, but <./export_spectra.py> will not work.


"""
Take spectrum library, and export the spectra in it in ASCII format.
"""

import os
from os import path as os_path
import argparse
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Spectrum library we should export. Stars may be filtered by parameters by placing a "
                         "comma-separated list of constraints in [] brackets after the name of the library. Use the "
                         "syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a range.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--output-stub', default="/tmp/my_spectra", dest='output_stub',
                    help="Directory to write output to.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

# Open spectrum library we're going to plot
input_library_info = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                           workspace=workspace,
                                                           extra_constraints={}
                                                           )
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
    filename_stub = os_path.join(args.output_stub, "{0}_{1}_{2:06.4f}_{3:06.1f}".format(metadata["Starname"],
                                                                                        metadata["continuum_normalised"],
                                                                                        metadata["e_bv"],
                                                                                        metadata["SNR"]))

    # Write metadata
    with open("{}.txt".format(filename_stub), "w") as f:
        for key in sorted(metadata.keys()):
            f.write("{0:12s}: {1}\n".format(key, metadata[key]))

    # Write spectrum
    with open("{}.spec".format(filename_stub), "w") as f:
        np.savetxt(f, np.asarray(zip(spectrum.wavelengths, spectrum.values, spectrum.value_errors)))

