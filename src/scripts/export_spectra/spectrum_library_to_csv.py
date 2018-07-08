#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python spectrum_library_to_csv.py>, but <./spectrum_library_to_csv.py> will not work.

"""
Take spectrum library, and output all of the metadata contained within into a CSV file.
"""

from os import path as os_path
import argparse
import re

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', dest='library', default="turbospec_ahm2017_sample",
                    help="Spectrum library we should export. Stars may be filtered by parameters by placing a "
                         "comma-separated list of constraints in [] brackets after the name of the library. Use the "
                         "syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a range.")
parser.add_argument('--separator', dest='separator', default=",",
                    help="Separator to use between fields.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "workspace")

# Open spectrum library we're going to plot
input_library_info = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                           workspace=workspace,
                                                           extra_constraints={"continuum_normalised": 0}
                                                           )
input_library, library_items = [input_library_info[i] for i in ("library", "items")]
library_ids = [i["specId"] for i in library_items]

# Fetch list of all metadata fields
fields = input_library.list_metadata_fields()
fields.sort()

# Write out information about spectra one by one
for i in range(len(library_ids)):
    metadata = input_library.get_metadata(ids=library_ids[i])[0]

    if i == 0:
        line = args.separator.join(fields)
        print line

    words = []
    for x in fields:
        word = metadata.get(x, "-")
        if type(word) not in [int, float]:
            word = "\"{}\"".format(re.sub("\"", "\\\"", str(word)))
        else:
            word = str(word)
        words.append(word)
    line = args.separator.join(words)
    print line
