#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python scatter_plot_coloured.py>, but <./scatter_plot_coloured.py> will not work.

"""
Take an output file from the Cannon, and produce a scatter plot of coloured points, with label values on the two axes
and the colour of the points representing the error in one of the derived labels.
"""

import os
import sys
import argparse
import re
import json
import numpy as np
from label_tabulator import tabulate_labels

from lib_multiplotter import make_multiplot

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should plot on the two axes of the scatter plot.")
parser.add_argument('--label-axis-latex', required=True, action="append", dest='label_axis_latex',
                    help="Titles we should put on the two axes of the scatter plot.")
parser.add_argument('--colour-by-label', required=True, dest='colour_label',
                    help="Label we should use to colour code points by the Cannon's offset from library values.")
parser.add_argument('--colour-range-min', required=True, dest='colour_range_min', type=float,
                    help="The range of parameter values to use in colouring points.")
parser.add_argument('--colour-range-max', required=True, dest='colour_range_max', type=float,
                    help="The range of parameter values to use in colouring points.")
parser.add_argument('--cannon-output',
                    required=True,
                    default="",
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--output-stub', default="/tmp/cannon_estimates_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Check that we have one label to plot on each axis label, and a title to show on each axis
assert len(args.labels) == 2, "A scatter plot needs two labels to plot -- one on each axis."
assert len(args.label_axis_latex) == 3, "A coloured scatter plot needs label names for two axes, plus the colour scale."

# Labels are supplied with ranges listed in {}. We extract the names to pass to label_tabulator.
label_list = []
label_names = []
for item in args.labels + [args.colour_label]:
    test = re.match("(.*){(.*:.*)}", item)
    assert test is not None, "Label names should take the form <name{:2}>, with range to plot in {}."
    label_list.append({
        "name": test.group(1),
        "range": test.group(2)
    })
    label_names.append(test.group(1))

# Fetch title for this Cannon run
if not os.path.exists(args.cannon):
        print "scatter_plot_coloured.py could not proceed: Cannon run <{}> not found".format(args.cannon)
        sys.exit()

cannon_output = json.loads(open(args.cannon).read())
description = cannon_output['description']

# Check that labels exist
for label in label_names:
    if label not in cannon_output["labels"]:
        print "scatter_plot_coloured.py could not proceed: Label <{}> not present in <{}>".format(label, args.cannon)
        sys.exit()

# Create data files listing parameter values
snr_list = tabulate_labels(args.output_stub, label_names, args.cannon)

# Convert SNR/pixel to SNR/A at 6000A
raster = np.array(cannon_output['wavelength_raster'])
raster_diff = np.diff(raster[raster > 6000])
pixels_per_angstrom = 1.0 / raster_diff[0]

# Create pyxplot script to produce this plot
width = 16
aspect = 1 / 1.618034  # Golden ratio
pyxplot_input = """

col_scale_z(z) = min(max(  (z-({0})) / (({1})-({0}))  ,0),1)

col_scale(z) = hsb(0.75 * col_scale_z(z), 1, 1)

""".format(args.colour_range_min, args.colour_range_max)

eps_list = []
for snr in snr_list:
    pyxplot_input += """
    
set nodisplay
set origin 0,0
set width {0}
set size ratio {1}
set term dpi 400
set nokey

set multiplot

set xlabel "Input {2}"
set xrange [{3}]
set ylabel "Input {4}"
set yrange [{5}]

set textvalign top
set label 1 "\\parbox{{{0}cm}}{{{6} \\newline {{\\bf {7} }} \\newline SNR/\\AA={9:.1f} \\newline SNR/pixel={8:.1f}}}" \
            at page 0.5, page {10}

""".format(width, aspect,
           args.label_axis_latex[0], label_list[0]["range"], args.label_axis_latex[1], label_list[1]["range"],
           description, args.label_axis_latex[2],
           snr["snr"],
           snr["snr"] * np.sqrt(pixels_per_angstrom),  # Convert SNR/pixel to SNR/A
           width * aspect - 0.3)

    pyxplot_input += """
    
set output "{0}.png"
clear
unset origin ; set axis y left ; unset xtics ; unset mxtics
plot "{0}" title "Offset in {1} at SNR {2}." with dots colour col_scale($6-$3) ps 8

""".format(snr["filename"], args.label_axis_latex[2], snr["snr"])

    pyxplot_input += """

unset label
set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y right
set ylabel "Offset in {0}"
set yrange [{1}:{2}]
set c1range [{1}:{2}] norenormalise
set width {3}
set size ratio 1 / 0.05
set colormap col_scale(c1)
set nocolkey
set sample grid 2x200
set origin {4}, 0
plot y with colourmap

""".format(args.label_axis_latex[2], args.colour_range_min, args.colour_range_max, width * aspect * 0.05, width + 1)

    pyxplot_input += """

set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh

""".format(snr["filename"])

    eps_list.append("{0}.eps".format(snr["filename"]))

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()

# Make multiplot
make_multiplot(eps_files=eps_list,
               output_filename="{0}_multiplot".format(args.output_stub),
               aspect=4.8 / 8
               )
