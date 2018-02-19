#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take spectrum library, and list some basic stellar parameters and photometry for the spectra within.
"""

from os import path as os_path
import argparse
import re
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Spectrum library we should export, with additional constraints if wanted.")
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
library_spectra = input_library.open(ids=library_ids)

# Write out spectra one by one
for i in range(len(library_spectra)):
    metadata = library_spectra.get_metadata(i)

    if "Starname" not in metadata:
        metadata["Starname"] = "untitled"

    spectrum = library_spectra.extract_item(i)

    name = metadata["Starname"]
    if metadata.get("exposure", np.nan) is None:
        metadata["exposure"] = np.nan
    exposure = float(metadata.get("exposure", np.nan))
    mag_4fs = float(metadata.get("magnitude", np.nan))
    reddening = float(metadata.get("e_bv", np.nan))
    snr = float(metadata.get("SNR", np.nan))
    snr_defn = metadata.get("snr_definition", "--")
    snr_per_unit = "pix" if (metadata.get("SNR_per", None) != "A") else "A"

    r = spectrum.photometry("SDSS_r")
    g = spectrum.photometry("SDSS_g")
    u = spectrum.photometry("SDSS_u")

    if ((("lrs" in args.library) and ((int(mag_4fs) in [13, 16]) or (int(snr) in [100, 150]))) or
            (("hrs" in args.library) and ((int(mag_4fs) in [15, 19]) or (int(snr) in [10, 50])))):
        continue

    if i == 0:
        line = "# {:13s} {:8s} {:8s} {:8s} {:8s} {:8s} {:8s} {:8s} {:10s}". \
            format("Object", "Exposure", "Mag(4FS)", "E(B-V)", "Teff", "log(g)", "[Fe/H]",
                   "SNR/" + snr_per_unit, "SNR defn")
        # line += " {:8s} {:8s} {:8s}".format("SDSS_r", "SDSS_g", "SDSS_u")
        print line

    line = "{:15s} {:8.1f} {:8.2f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.1f} {:10s}". \
        format(name, exposure, mag_4fs, reddening, metadata["Teff"], metadata["logg"], metadata["[Fe/H]"],
               snr, snr_defn)
    # line += " {:8.3f} {:8.3f} {:8.3f}".format(r, g, u)
    print line
