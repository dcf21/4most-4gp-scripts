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
                    help="The name of the spectrum library we are to read input spectra from. A subset of the stars "
                         "in the input library may optionally be selected by suffixing its name with a comma-separated "
                         "list of constraints in [] brackets. Use the syntax my_library[Teff=3000] to demand equality, "
                         "or [0<[Fe/H]<0.2] to specify a range. We do not currently support other operators like "
                         "[Teff>5000], but such ranges are easy to recast is a range, e.g. [5000<Teff<9999].")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--output-stub', default="/tmp/my_spectra", dest='output_stub',
                    help="Directory to write ASCII representations of spectra into.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")

# Open spectrum library we're going to export from, and search for flux-normalised spectra meeting our filtering
# constraints
input_library_info = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                           workspace=workspace,
                                                           extra_constraints={}
                                                           )

# Get a list of the spectrum IDs which we were returned
input_library, library_items = [input_library_info[i] for i in ("library", "items")]
library_ids = [i["specId"] for i in library_items]
library_spectra = input_library.open(ids=library_ids)

# Create output directory
os.system("mkdir -p {}".format(args.output_stub))

# Write out spectra one by one
for i in range(len(library_spectra)):
    # Retrieve the dictionary of metadata associated with this spectrum
    metadata = library_spectra.get_metadata(i)

    # Retrieve the spectrum itself
    spectrum = library_spectra.extract_item(i)

    # Create a filename to save an ASCII version of this spectrum to
    filename_stub = os_path.join(args.output_stub, "{star_name}_{normalisation}_{reddening:06.4f}_{snr:06.1f}".
                                 format(star_name=metadata.get("Starname", "untitled"),
                                        normalisation=metadata.get("continuum_normalised", 0),
                                        reddening=metadata.get("e_bv", 0),
                                        snr=metadata.get("SNR", 0))
                                 )

    # Write a text file containing the metadata associated with this spectrum
    with open("{filename}.txt".format(filename=filename_stub), "w") as f:
        for key in sorted(metadata.keys()):
            f.write("{keyword:12s}: {value}\n".format(keyword=key, value=metadata[key]))

    # Write a text file containing the spectrum itself
    with open("{filename}.spec".format(filename=filename_stub), "w") as f:
        np.savetxt(f, np.asarray(zip(spectrum.wavelengths, spectrum.values, spectrum.value_errors)))
