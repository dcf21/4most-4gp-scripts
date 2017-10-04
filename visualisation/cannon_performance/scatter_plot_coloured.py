#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take an output file from the Cannon, and produce a scatter plot of coloured points, with label values on the two axes
and the colour of th points representing the error in one of the derived labels.
"""

import os
import argparse
import re
from label_tabulator import tabulate_labels

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
parser.add_argument('--cannon_output',
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

# Create data files listing parameter values
snr_list = tabulate_labels(args.output_stub, label_names, args.cannon)

# Create pyxplot script to produce this plot
width = 14
aspect = 1 / 1.618034  # Golden ratio
pyxplot_input = """

col_scale_z(z) = min(max(  (z-({0})) / (({1})-({0}))  ,0),1)

col_scale(z) = hsb(0.75 * col_scale_z(z), 1, 1)

""".format(args.colour_range_min, args.colour_range_max)

for snr in snr_list:
    pyxplot_input += """
    
set nodisplay
set origin 0,0
set width {}
set size ratio {}
set nokey

set multiplot

set xlabel "{}"
set xrange [{}]
set ylabel "{}"
set yrange [{}]

""".format(width, aspect,
           args.label_axis_latex[0], label_list[0]["range"], args.label_axis_latex[1], label_list[1]["range"])

    pyxplot_input += """
    
set output "{0}.png"
clear
unset origin ; set axis y left ; unset xtics ; unset mxtics
plot "{0}" title "Offset in {1} at SNR {2}." with dots colour col_scale($6-$3) ps 5

""".format(snr["filename"], args.label_axis_latex[2], snr["snr"])

    pyxplot_input += """

set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y right
set ylabel "{0}"
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

set term eps ; set output "{0}.eps" ; set display ; refresh
set term png ; set output "{0}.png" ; set display ; refresh
set term pdf ; set output "{0}.pdf" ; set display ; refresh

""".format(snr["filename"])

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
