#!../../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python scatter_plot_cannon_uncertainty.py>, but <./scatter_plot_cannon_uncertainty.py> will not work.

"""
Take an output file from the Cannon, and produce a scatter plot of the offset in each label, as a function of the
uncertainty that the Cannon quotes.
"""

import os
import sys
import re
import argparse
import gzip
import json
import numpy as np
from label_tabulator import tabulate_labels

from lib.pyxplot_driver import PyxplotDriver
from lib.label_information import LabelInformation
from lib.plot_settings import snr_defined_at_wavelength, plot_width
from fourgp_degrade import SNRConverter

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cannon-output',
                    required=True,
                    dest='cannon',
                    help="Filename of the JSON file containing the label values estimated by the Cannon, without "
                         "the <.summary.json.gz> suffix.")
parser.add_argument('--output', default="/tmp/scatter_plot_cannon_uncertainty", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Fetch title for this Cannon run
if not os.path.exists(args.cannon + ".summary.json.gz"):
    print "scatter_plot_cannon_uncertainty.py could not proceed: Cannon run <{}> not found". \
        format(args.cannon + ".summary.json.gz")
    sys.exit()

cannon_output = json.loads(gzip.open(args.cannon + ".summary.json.gz").read())
description = cannon_output['description']

# Work out multiplication factor to convert SNR/pixel to SNR/A
snr_converter = SNRConverter(raster=np.array(cannon_output['wavelength_raster']),
                             snr_at_wavelength=snr_defined_at_wavelength)

# Metadata about all the labels which we can plot the Cannon's precision in estimating
label_metadata = LabelInformation().label_metadata

# Look up list of labels the Cannon was fitting
label_names = [item for item in cannon_output['labels'] if item in label_metadata]
label_count = len(label_names)

# Create data files listing parameter values
snr_list = tabulate_labels(output_stub="{}/uncertainty_snr_".format(args.output_stub),
                           labels=label_names,
                           cannon=args.cannon)

# Create pyxplot script to produce this plot
plotter = PyxplotDriver(multiplot_filename="{0}/uncertainty_multiplot".format(args.output_stub),
                        width=plot_width * 1.3,
                        multiplot_aspect=6. / 8)

for index, label in enumerate(label_names):
    label_info = label_metadata[label]
    plotter.make_plot(output_filename="{0}/uncertainty_{1}".format(args.output_stub, index),
                      data_files=[snr["filename"] for snr in snr_list],
                      caption=r"""
{description} \newline {{\bf {label_name} }}
""".format(description=re.sub("_", r"\_", description),
           label_name=label_info['latex']
           ).strip(),
                      pyxplot_script="""

col_scale(z) = hsb(0.75 * z, 1, 1)
    
set numerics errors quiet
set key top right

set xlabel "Cannon estimated uncertainty in {label_name}"
# set xrange [0:{label_range}]
set ylabel "$\Delta$ {label_name}"
set yrange [-{label_range}:{label_range}]

plot {plot_items}

""".format(label_name=label,
           label_range=1000 if label == "Teff" else 2,
           plot_items=", ".join(["""
"{filename}" using {column_x}:(${column_y_1}-${column_y_2}) title "SNR {snr:.1f}" \
             with dots colour col_scale({colour_value}) ps 5
           """.format(filename=snr["filename"],
                      column_x=3 * index + 3,
                      column_y_1=3 * index + 1,
                      column_y_2=3 * index + 2,
                      snr=snr_converter.per_pixel(snr["snr"]).per_a(),
                      colour_value=index2 / max(float(len(snr_list) - 1), 1)
                      ).strip()
                                 for index2, snr in enumerate(snr_list)
                                 ]))
                      )

# Clean up plotter
del plotter
