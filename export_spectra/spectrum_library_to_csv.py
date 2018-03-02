#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

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
                    help="Spectrum library we should export, with additional constraints if wanted.")
parser.add_argument('--separator', dest='separator', default=",",
                    help="Separator to use between fields.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
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
    constraints["continuum_normalised"] = 0  # All input spectra must be continuum normalised
    library_path = os_path.join(workspace, library_name)
    input_library = SpectrumLibrarySqlite(path=library_path, create=False)
    library_items = input_library.search(**constraints)
    return {
        "library": input_library,
        "items": library_items
    }


# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "workspace")

# Open spectrum library we're going to plot
input_library_info = open_input_libraries(args.library, {})
input_library, library_items = [input_library_info[i] for i in ("library", "items")]
library_ids = [i["specId"] for i in library_items]

# Fetch list of all metadata fields
fields = input_library.list_metadata_fields()
fields.sort()

# Write out information about spectra one by one
for i in range(len(library_ids)):
    metadata = input_library.get_metadata(ids=library_ids[i])[0]

    if i == 0:
        line = "# " + " ".join(fields)
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
