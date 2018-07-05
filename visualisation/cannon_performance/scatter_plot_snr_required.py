#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python scatter_plot_snr_required.py>, but <./scatter_plot_snr_required.py> will not work.

"""
Take an output file from the Cannon, and produce a scatter plot of coloured points, with label values on the two axes
and the colour of the points representing the SNR needed to attain some required level of accuracy in a third label.
"""

import os
from os import path as os_path
import sys
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
parser.add_argument('--cannon-output',
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
if not os.path.exists(args.cannon):
        print "scatter_plot_snr_required.py could not proceed: Cannon run <{}> not found".format(args.cannon)
        sys.exit()

cannon_output = json.loads(open(args.cannon).read())

# Check that labels exist
for label in label_names:
    if label not in cannon_output["labels"]:
        print "scatter_plot_snr_required.py could not proceed: Label <{}> not present in <{}>".\
            format(label, args.cannon)
        sys.exit()

if args.colour_label not in cannon_output["labels"]:
        print "scatter_plot_snr_required.py could not proceed: Label <{}> not present in <{}>".\
            format(args.colour_label, args.cannon)
        sys.exit()

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
    if object_name not in star_names:
        continue
    if object_name not in offsets:
        offsets[object_name] = {}
    try:
        offsets[object_name][star['SNR']] = abs(star[args.colour_label] - star["target_{}".format(args.colour_label)])
        if object_name not in label_values:
            label_values[object_name] = [star["target_{}".format(item)] for item in label_names]
    except KeyError:
        # If this star has missing data for one of the labels being measured, discard it
        star_names.remove(object_name)
        offsets.pop(object_name, None)  # Delete if exists
        label_values.pop(object_name, None)

# Loop over stars, calculating the SNR needed for each one
output = []
for star_name in star_names:
    if star_name in offsets:
        snr_required_per_a = 1e6
        previous_offset = 1e6
        previous_snr = 0
        for snr in snr_values:
            new_offset = offsets[star_name][snr]
            if (new_offset <= args.target_accuracy) and (previous_offset > args.target_accuracy):
                weight_a = abs(new_offset - args.target_accuracy)
                weight_b = abs(previous_offset - args.target_accuracy)
                snr_required_per_pixel = (previous_snr * weight_a + snr * weight_b) / (weight_a + weight_b)
                snr_required_per_a = snr_required_per_pixel * sqrt(pixels_per_angstrom)
            previous_offset = new_offset
            previous_snr = snr
        output.append(label_values[star_name] + [snr_required_per_a])

# Make sure that output directory exists
os.system("mkdir -p {}".format(os_path.split(args.output_stub)[0]))

# Write values to data files
# Each line is in the format <x  y  SNR/A>
filename = "{}.dat".format(args.output_stub)
with open(filename, "w") as f:
    for line in output:
        f.write("%16s %16s %16s\n" % tuple(line))

# Create pyxplot script to produce this plot
width = 16
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
set term dpi 400
set fontsize 1.1
set nokey

set multiplot

set xlabel "Input {}"
set xrange [{}]
set ylabel "Input {}"
set yrange [{}]

# set label 1 "{}" at page 0.5, page {}

""".format(width, aspect,
           args.label_axis_latex[0], label_list[0]["range"], args.label_axis_latex[1], label_list[1]["range"],
           cannon_output['description'], width * aspect - 0.5)

pyxplot_input += """
    
set output "{0}.png"
clear
unset origin ; set axis y left ; unset xtics ; unset mxtics
plot "{0}" title "SNR needed to achieve accuracy of {1} {2} in {3}" with dots colour col_scale($3) ps 8

""".format(filename, args.target_accuracy, args.accuracy_unit, args.label_axis_latex[2])

pyxplot_input += """

unset label
set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y y2 right
set ylabel "SNR/\AA (at 6000\AA) needed to achieve accuracy of {1} {2} in {0}"
set yrange [{3}:{4}]
set y2label "SNR/pixel (at 6000\AA)"
set y2range [{3}/{7}:{4}/{7}]
set c1range [{3}:{4}] norenormalise
set width {5}
set size ratio 1 / 0.05
set colormap col_scale(c1)
set nocolkey
set sample grid 2x200
set origin {6}, 0
plot y with colourmap

""".format(args.label_axis_latex[2], args.target_accuracy, args.accuracy_unit,
           args.colour_range_min, args.colour_range_max, width * aspect * 0.05, width + 1,
           sqrt(pixels_per_angstrom))

pyxplot_input += """

set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh

""".format(filename)

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
