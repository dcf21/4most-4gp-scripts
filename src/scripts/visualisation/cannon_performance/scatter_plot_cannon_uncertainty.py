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
import argparse
import json
import numpy as np
from label_tabulator import tabulate_labels

from lib.pyxplot_driver import PyxplotDriver
from lib.plot_settings import snr_defined_at_wavelength
from lib.snr_conversion import SNRConverter

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cannon-output',
                    required=True,
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--output', default="/tmp/cannon_uncertainty_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Fetch title for this Cannon run
if not os.path.exists(args.cannon):
    print "scatter_plot_cannon_uncertainty.py could not proceed: Cannon run <{}> not found".format(args.cannon)
    sys.exit()

cannon_output = json.loads(open(args.cannon).read())
description = cannon_output['description']

# Work out multiplication factor to convert SNR/pixel to SNR/A
snr_converter = SNRConverter(raster=np.array(cannon_output['wavelength_raster']),
                             snr_at_wavelength=snr_defined_at_wavelength)

# Look up list of labels the Cannon was fitting
label_names = cannon_output['labels']
label_count = len(label_names)

# Create data files listing parameter values
snr_list = tabulate_labels(args.output_stub, label_names, args.cannon)

# Create pyxplot script to produce this plot
plotter = PyxplotDriver(multiplot_filename="{0}_multiplot".format(args.output_stub),
                        multiplot_aspect=6. / 8)

for index, label in enumerate(label_names):
    plotter.make_plot(output_filename="{0}_{1}".format(args.output_stub, index),
                      caption=r"""
{description} \newline {{\bf {label_name} }}
""".format(description=description, label_name=label).strip(),
                      pyxplot_script="""

col_scale(z) = hsb(0.75 * z, 1, 1)
    
set key bottom left

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
                      column_x=2 * label_count + index + 1,
                      column_y_1=index + 1,
                      column_y_2=label_count + index + 1,
                      snr=snr_converter.per_pixel(snr["snr"]).per_a(),
                      colour_value=index2 / max(float(len(snr_list) - 1), 1)).strip()
                       for index2, snr in enumerate(snr_list)
                       ]))
                      )

# Clean up plotter
del plotter
