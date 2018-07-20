#!../../../../virtualenv/bin/python2.7
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
                    help="The name of the spectrum library we are to read input spectra from. A subset of the stars "
                         "in the input library may optionally be selected by suffixing its name with a comma-separated "
                         "list of constraints in [] brackets. Use the syntax my_library[Teff=3000] to demand equality, "
                         "or [0<[Fe/H]<0.2] to specify a range. We do not currently support other operators like "
                         "[Teff>5000], but such ranges are easy to recast is a range, e.g. [5000<Teff<9999].")
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
library_spectra = input_library.open(ids=library_ids)

# Write out information about each spectrum, one by one
for i in range(len(library_spectra)):
    # Retrieve the dictionary of metadata associated with this spectrum
    metadata = library_spectra.get_metadata(i)

    # Retrieve the spectrum itself
    spectrum = library_spectra.extract_item(i)

    # Retrieve information about this spectrum, with default values for any metadata which is missing
    name = metadata.get("Starname", "untitled")

    # Note that the exposure and magnitude fields are only set on spectra which have passed through 4FS. The exposure
    # may be None rather than NaN if the field exists in the database but has no value set.
    if metadata.get("exposure", np.nan) is None:
        metadata["exposure"] = np.nan

    # The SNR field is only set on spectra which have had synthetic noise added
    snr = float(metadata.get("SNR", np.nan))
    snr_defn = metadata.get("snr_definition", "--")
    snr_per_unit = "pix" if (metadata.get("SNR_per", None) != "A") else "A"

    # Do some basic photometry on the spectrum so we can report how bright it is
    r = spectrum.photometry("SDSS_r")
    g = spectrum.photometry("SDSS_g")
    u = spectrum.photometry("SDSS_u")

    # Can do some extra filtering at this stage if we want to reduce the amount of output...
    # if ((("lrs" in args.library) and ((int(mag_4fs) in [13, 16]) or (int(snr) in [100, 150]))) or
    #         (("hrs" in args.library) and ((int(mag_4fs) in [15, 19]) or (int(snr) in [10, 50])))):
    #     continue

    # Write out some column headings at the beginning of the output
    if i == 0:
        line = "# {:13s} {:8s} {:8s} {:8s} {:8s} {:8s} {:8s} {:8s} {:10s}". \
            format("Object", "Exposure", "Mag(4FS)", "E(B-V)", "Teff", "log(g)", "[Fe/H]",
                   "SNR/" + snr_per_unit, "SNR defn")
        line += " {:8s} {:8s} {:8s}".format("SDSS_r", "SDSS_g", "SDSS_u")
        print line

    # Write out a row of data
    line = "{:15s} {:8.1f} {:8.2f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.1f} {:10s}". \
        format(name,
               float(metadata.get("exposure", np.nan)),
               float(metadata.get("magnitude", np.nan)),
               float(metadata.get("e_bv", np.nan)),  # Only set if passed through <degrade_spectra/redden_library.py>
               float(metadata.get("Teff", np.nan)),
               float(metadata.get("logg", np.nan)),
               float(metadata.get("[Fe/H]", np.nan)),
               snr, snr_defn)
    line += " {:8.3f} {:8.3f} {:8.3f}".format(r, g, u)
    print line
