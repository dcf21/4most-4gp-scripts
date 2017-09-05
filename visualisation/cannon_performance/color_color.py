#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take a SpectrumLibrary and tabulate the stellar parameters within it.
"""

import argparse
from os import path as os_path

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Library of spectra we should output stellar labels for.")
parser.add_argument('--cannon_output',
                    required=False,
                    default="",
                    dest='cannon',
                    help="Cannon output file.")
parser.add_argument('--output-file', default="/tmp/label_values.dat", dest='output_file',
                    help="Data file to write output to.")
args = parser.parse_args()

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "..", "workspace")

SNRs = [5, 10, 15, 20, 50, 100, 250]

output = {}

# Open output data file
for SNR in SNRs:
    filename = "{}{:03d}.dat".format(args.output_file, SNR)
    with open(filename, "w") as output_file:
        # Open spectrum libraries in turn
        library_path = os_path.join(workspace, args.library)
        library_object = SpectrumLibrarySqlite(path=library_path, create=False)

        # Loop over objects in each spectrum library
        for item in library_object.search(continuum_normalised=1, SNR=250):
            metadata = library_object.get_metadata(ids=item['specId'])[0]
            output[metadata['Starname']] = [metadata['Teff'], metadata['logg']]

        if args.cannon:
            for line in open(args.cannon):
                words = line.split()
                item_Starname = words[18]
                if item_Starname == "Starname":
                    continue
                item_SNR = float(words[17])
                item_Teff = words[19]
                item_logg = words[35]

                if item_SNR == SNR and item_Starname in output:
                    output[item_Starname].append(item_Teff)
                    output[item_Starname].append(item_logg)

        for key, value in output.iteritems():
            output_file.write(" ".join([str(i) for i in value]) + "\n")


"""
python color_color.py --library 4fs_apokasc_test_set_hrs --output-file /tmp/tg_test_hrs_ --cannon_output ../../output_data/cannon_test_4fs_hrs.dat 
python color_color.py --library 4fs_apokasc_test_set_lrs --output-file /tmp/tg_test_lrs_ --cannon_output ../../output_data/cannon_test_4fs_lrs.dat 
python color_color.py --library 4fs_apokasc_training_set_hrs --output-file /tmp/tg_train_hrs_
python color_color.py --library 4fs_apokasc_training_set_lrs --output-file /tmp/tg_train_lrs_


set term png dpi 200
set width 25
set key top left
set xlabel "Teff"
set xrange [5100:4000]
set ylabel "log(g)"
set yrange [3.8:1.2]
set linewidth 0.4
set output /tmp/tg_plot_training_set.png
plot "/tmp/tg_train_lrs_250.dat" title "Training set" using $1:$2 with dots c red ps 8
set output /tmp/tg_plot_test_set.png
plot "/tmp/tg_test_lrs_250.dat" title "Test set" using $1:$2 with dots c red ps 8
set output /tmp/tg_plot_test_set_lrs.png
plot "/tmp/tg_test_lrs_100.dat" title "LRS Test output, SNR 100." using $3:$4 with dots c red ps 8
set output /tmp/tg_plot_test_set_hrs.png
plot "/tmp/tg_test_hrs_100.dat" title "HRS Test output, SNR 100." using $3:$4 with dots c red ps 8

foreach mode in ["lrs","hrs"] {
foreach snr in ["005","010","015","020","050","100","250"] {
set output "/tmp/tg_plot_test_output_%s_%s.png"%(mode,snr)
plot "/tmp/tg_test_%s_%s.dat"%(mode,snr) title "Cannon output -$>$ Synthesised values. %s, SNR %s."%(mode,snr) with arrows c red using 3:4:1:2
}
}

"""