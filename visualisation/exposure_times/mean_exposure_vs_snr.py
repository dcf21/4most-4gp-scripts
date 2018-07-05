#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python mean_exposure_vs_snr.py>, but <./mean_exposure_vs_snr.py> will not work.

"""
Take a SpectrumLibrary and tabulate the average exposure time at each SNR within it.
"""

import argparse
import os
import time
from os import path as os_path
import pwd
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Library of spectra we should output stellar labels for.")
parser.add_argument('--wavelength', required=True, dest='wavelength',
                    help="Wavelength to use for converting SNR/pixel to SNR/A")
parser.add_argument('--output-file', default="/tmp/exposure_times_vs_snr.dat", dest='output_file',
                    help="Data file to write output to.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "..", "workspace")

# Construct list of exposure times at each SNR
exposures_by_snr = {}

# Raster on which data is sampled
raster = None
raster_diff = None
pixels_per_angstrom = None

# Open output data file
with open(args.output_file, "w") as output:

        # Open spectrum library
        spectra = SpectrumLibrarySqlite.open_and_search(
          library_spec=args.library,
          workspace=workspace,
          extra_constraints={"continuum_normalised": 1}
         )
        library_object, library_items = [spectra[i] for i in ("library", "items")]

        # Loop over objects in SpectrumLibrary
        for item in library_items:

            # Convert SNR/pixel to SNR/A
            if raster is None:
                if float(args.wavelength) > 0:
                    spectrum = library_object.open(ids=item['specId']).extract_item(0)
                    raster = spectrum.wavelengths
                    raster_diff = np.diff(raster[raster > float(args.wavelength)])
                    pixels_per_angstrom = 1.0 / raster_diff[0]
                else:
                    pixels_per_angstrom = 1

            metadata = library_object.get_metadata(ids=item['specId'])[0]

            exposure = metadata['exposure']
            snr = metadata['SNR']

            if snr not in exposures_by_snr:
                exposures_by_snr[snr] = []

            exposures_by_snr[snr].append(exposure)

# Make list of unique SNR values
unique_snrs = set(exposures_by_snr.keys())
unique_snrs_sorted = list(unique_snrs)
unique_snrs_sorted.sort()

# Write output data file
with open(args.output_file,"w") as f:
    f.write("# SNR/pixel  SNR/A  Mean_exposure_time  StdDev_of_exposure_times\n")
    for snr in unique_snrs_sorted:
        f.write("{0:.3f}  {1:.3f}  {2:.3f}  {3:.3f}\n".format(snr, snr * np.sqrt(pixels_per_angstrom),
                                                              np.mean(exposures_by_snr[snr]),
                                                              np.std(exposures_by_snr[snr])))

# Produce plot of exposure time versus SNR
stem = args.output_file
aspect = 1 / 1.618034  # Golden ratio
plot_width = 18
date_stamp = True

user_name = pwd.getpwuid( os.getuid() ).pw_gecos.split(",")[0]
plot_creator = "{}, {}".format(user_name, time.strftime("%d %b %Y"))

with open("{}.ppl".format(stem), "w") as ppl:
    ppl.write("""
    
    set width {0}
    set size ratio {1}
    set term dpi 400
    set nodisplay ; set multiplot
    set label 1 texifyText("{2} ({3} stars)") page {4}, page 1
    
    """.format(plot_width, aspect,
               args.library,
               len(exposures_by_snr[unique_snrs_sorted[0]]),
               plot_width * 0.2))

    if date_stamp:
        ppl.write("""
        set fontsize 0.8
        text "{}" at 0, {}
        """.format(plot_creator, plot_width * aspect + 0.4))

    ppl.write("set fontsize 1.3\n")  # 1.6
    ppl.write("set nokey\n")
    ppl.write("set ylabel \"Exposure time [min]\"\n")
    ppl.write("set xlabel \"SNR/\AA\"\n")

    # Set axis limits
    ppl.write("set yrange [1:2000] ; set log y\n")
    ppl.write("set xrange [0:250]\n")

    ppl.write("plot '{}' with yerrorbars using 2:3:4\n".format(args.output_file))

    ppl.write("""
    
    set term eps ; set output '{0}.eps' ; set display ; refresh
    set term png ; set output '{0}.png' ; set display ; refresh
    set term pdf ; set output '{0}.pdf' ; set display ; refresh

    """.format(stem))
os.system("pyxplot {}.ppl".format(stem))
