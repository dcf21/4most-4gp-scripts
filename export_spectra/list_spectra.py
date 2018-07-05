#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python list_spectra.py>, but <./list_spectra.py> will not work.

"""
Take spectrum library, and list some basic stellar parameters and photometry for the spectra within.
"""

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
