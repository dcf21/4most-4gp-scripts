#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take an output file from the Cannon, and produce a scatter plot of coloured points, with label values on the two axes
and the colour of the points representing the SNR needed to attain some required level of accuracy in a third label.
"""

import os
import argparse
import re
import json
from math import sqrt
import numpy as np

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should plot on the two axes of the scatter plot.")
parser.add_argument('--label-axis-latex', required=True, action="append", dest='label_axis_latex',
                    help="Titles we should put on the two axes of the scatter plot.")
parser.add_argument('--colour-by-label', required=True, dest='colour_label',
                    help="Label we should use to colour code points by the SNR needed to achieve some "
                         "nominal accuracy in that label.")
parser.add_argument('--target-accuracy', required=True, dest='target_accuracy', type=float,
                    help="The target accuracy in the label we are colour-coding.")
parser.add_argument('--colour-range-min', required=True, dest='colour_range_min', type=float,
                    help="The range of SNR values to use in colouring points.")
parser.add_argument('--colour-range-max', required=True, dest='colour_range_max', type=float,
                    help="The range of SNR values to use in colouring points.")
parser.add_argument('--cannon_output',
                    required=True,
                    default="",
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--output-stub', default="/tmp/cannon_estimates_", dest='output_stub',
                    help="Data file to write output to.")
parser.add_argument('--accuracy-unit', default="apples", dest='accuracy_unit',
                    help="Unit to put after target accuracy we're aiming to achieve in label")
args = parser.parse_args()

# Check that we have one label to plot on each axis label, and a title to show on each axis
assert len(args.labels) == 2, "A scatter plot needs two labels to plot -- one on each axis."
assert len(args.label_axis_latex) == 3, "A coloured scatter plot needs label names for two axes, plus the colour scale."

# Labels are supplied with ranges listed in {}. We extract the names to pass to label_tabulator.
label_list = []
label_names = []
for item in args.labels:
    test = re.match("(.*){(.*:.*)}", item)
    assert test is not None, "Label names should take the form <name{:2}>, with range to plot in {}."
    label_list.append({
        "name": test.group(1),
        "range": test.group(2)
    })
    label_names.append(test.group(1))

# Read Cannon output
cannon_output = json.loads(open(args.cannon).read())

# Create a sorted list of all the SNR values we've got
snr_values = [item['SNR'] for item in cannon_output['stars']]
snr_values = sorted(set(snr_values))

# Create a sorted list of all the stars we've got
star_names = [item['Starname'] for item in cannon_output['stars']]
star_names = sorted(set(star_names))

# Work out multiplication factor to convert SNR/pixel to SNR/A
raster = np.array(cannon_output['wavelength_raster'])
raster_diff = np.diff(raster[raster > 6000])
pixels_per_angstrom = 1.0 / raster_diff[0]

# Loop over stars, calculating offsets for the label we're colour-coding
offsets = {}  # offsets[star_name][SNR] = dictionary of label names and absolute offsets
label_values = {}  # label_values[star_name] = list of label values on x and y axes
for star in cannon_output['stars']:
    object_name = star['Starname']
    if object_name not in offsets:
        offsets[object_name] = {}
    offsets[object_name][star['SNR']] = abs(star[args.colour_label] - star["target_{}".format(args.colour_label)])
    label_values[object_name] = [star["target_{}".format(item)] for item in label_names]

# Loop over stars, calculating the SNR needed for each one
output = []
for star_name in star_names:
    snr_required_per_a = 1e6
    previous_offset = 1e6
    previous_snr = 0
    for snr in snr_values:
        new_offset = offsets[star_name][snr]
        if new_offset > args.target_accuracy:
            previous_offset = new_offset
            previous_snr = snr
            continue
        weight_a = abs(new_offset - args.target_accuracy)
        weight_b = abs(previous_offset - args.target_accuracy)
        snr_required_per_pixel = (previous_snr * weight_a + snr * weight_b) / (weight_a + weight_b)
        snr_required_per_a = snr_required_per_pixel * sqrt(pixels_per_angstrom)
        break
    output.append(label_values[star_name] + [snr_required_per_a])

# Write values to data files
filename = "{}.dat".format(args.output_stub)
with open(filename, "w") as f:
    for line in output:
        f.write("%16s %16s %16s\n" % tuple(line))

# Create pyxplot script to produce this plot
width = 18
aspect = 1 / 1.618034  # Golden ratio
pyxplot_input = """

col_scale_z(z) = min(max(  (z-({0})) / (({1})-({0}))  ,0),1)

col_scale(z) = (z>{1}) ? colors.black : hsb(0.75 * col_scale_z(z), 1, 1)

""".format(args.colour_range_min, args.colour_range_max)

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

set label 1 "{}" at page 0.5, page {}

""".format(width, aspect,
           args.label_axis_latex[0], label_list[0]["range"], args.label_axis_latex[1], label_list[1]["range"],
           cannon_output['description'], width*aspect-0.5)

pyxplot_input += """
    
set output "{0}.png"
clear
unset origin ; set axis y left ; unset xtics ; unset mxtics
plot "{0}" title "SNR needed to achieve accuracy of {1} {2} in {3}." with dots colour col_scale($3) ps 5

""".format(filename, args.target_accuracy, args.accuracy_unit, args.label_axis_latex[2])

pyxplot_input += """

unset label
set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y right
set ylabel "SNR/\AA (at 6000\AA) needed for {0}"
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

""".format(filename)

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
