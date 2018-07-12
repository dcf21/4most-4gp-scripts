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
                    help="The name of the spectrum library we are to read input spectra from. A subset of the stars "
                         "in the input library may optionally be selected by suffixing its name with a comma-separated "
                         "list of constraints in [] brackets. Use the syntax my_library[Teff=3000] to demand equality, "
                         "or [0<[Fe/H]<0.2] to specify a range. We do not currently support other operators like "
                         "[Teff>5000], but such ranges are easy to recast is a range, e.g. [5000<Teff<9999].")
parser.add_argument('--separator', dest='separator', default=",",
                    help="Separator to use between fields in the CSV output.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

# Open spectrum library we're going to export from, and search for flux-normalised spectra meeting our filtering
# constraints
input_library_info = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                           workspace=workspace,
                                                           extra_constraints={"continuum_normalised": 0}
                                                           )

# Get a list of the spectrum IDs which we were returned
input_library, library_items = [input_library_info[i] for i in ("library", "items")]
library_ids = [i["specId"] for i in library_items]

# Fetch list of all metadata fields, and sort it alphabetically
fields = input_library.list_metadata_fields()
fields.sort()

# At the top of the CSV file, write column headings with the field names
line = args.separator.join(fields)
print line

# Write out information about spectra one by one
for i in range(len(library_ids)):
    # Fetch a dictionary of metadata about this spectrum
    metadata = input_library.get_metadata(ids=library_ids[i])[0]

    # Extract each field from the metadata in turn. Write a "-" when a field is not set on a particular spectrum.
    words = []
    for x in fields:
        word = metadata.get(x, "-")
        # For string metadata, make sure that quotes are escaped correctly in the CSV output
        if type(word) not in [int, float]:
            word = "\"{}\"".format(re.sub("\"", "\\\"", str(word)))
        else:
            word = str(word)
        words.append(word)

    # Print out a line of CSV output
    line = args.separator.join(words)
    print line
