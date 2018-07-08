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
import numpy as np

from lib.label_information import LabelInformation
from lib.multiplotter import PyxplotDriver
from lib.snr_conversion import SNRConverter

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should plot on the two axes of the scatter plot.")
parser.add_argument('--colour-by-label', required=True, dest='colour_by_label',
                    help="Label we should use to colour code points by the SNR needed to achieve some "
                         "nominal accuracy in that label.")
parser.add_argument('--target-accuracy', required=True, dest='target_accuracy', type=float,
                    help="The target accuracy in the label we are colour-coding.")
parser.add_argument('--colour-range-min', required=True, dest='colour_range_min', type=float,
                    help="The range of SNR/pixel values to use in colouring points.")
parser.add_argument('--colour-range-max', required=True, dest='colour_range_max', type=float,
                    help="The range of SNR/pixel values to use in colouring points.")
parser.add_argument('--cannon-output',
                    required=True,
                    default="",
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--output', default="/tmp/cannon_estimates_", dest='output_stub',
                    help="Data file to write output to.")
parser.add_argument('--accuracy-unit', default="apples", dest='accuracy_unit',
                    help="Unit to put after target accuracy we're aiming to achieve in label")
args = parser.parse_args()

# Check that we have one label to plot on each axis label, and a title to show on each axis
assert len(args.labels) == 2, "A scatter plot needs two labels to plot -- one on each axis."

# Label information
label_information = LabelInformation().label_info

# Labels are supplied with ranges listed in {}. We extract the names to pass to label_tabulator.
label_list = []
for item in args.labels + [args.colour_by_label]:
    test = re.match("(.*){(.*:.*)}", item)
    assert test is not None, "Label names should take the form <name{:2}>, with range to plot in {}."
    label_list.append({
        "name": test.group(1),
        "latex": label_information[test.group(1)]["latex"],
        "range": test.group(2),
        "min": test.group(2).split(":")[0],
        "max": test.group(2).split(":")[1]
    })

# Read Cannon output
if not os.path.exists(args.cannon):
    print "scatter_plot_snr_required.py could not proceed: Cannon run <{}> not found".format(args.cannon)
    sys.exit()

cannon_output = json.loads(open(args.cannon).read())

# Check that labels exist
for label in label_list:
    if label["name"] not in cannon_output["labels"]:
        print "scatter_plot_snr_required.py could not proceed: Label <{}> not present in <{}>".format(label["name"],
                                                                                                      args.cannon)
        sys.exit()

# Create a sorted list of all the SNR values we've got
snr_values = [item['SNR'] for item in cannon_output['stars']]
snr_values = sorted(set(snr_values))

# Create a sorted list of all the stars we've got
star_names = [item['Starname'] for item in cannon_output['stars']]
star_names = sorted(set(star_names))

# Work out multiplication factor to convert SNR/pixel to SNR/A
snr_converter = SNRConverter(raster=np.array(cannon_output['wavelength_raster']),
                             snr_at_wavelength=6100)

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
        offsets[object_name][star['SNR']] = abs(star[args.colour_by_label] -
                                                star["target_{}".format(args.colour_by_label)])
        if object_name not in label_values:
            label_values[object_name] = [star["target_{}".format(item['name'])] for item in label_list]
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
                snr_required_per_a = snr_converter.per_pixel(snr_required_per_pixel).per_a()
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
plotter = PyxplotDriver()

plotter.make_plot(output_filename=filename,
                  caption=cannon_output['description'],
                  pyxplot_script="""

col_scale_z(z) = min(max(  (z-({colour_range_min_per_pixel})) / \
                 (({colour_range_max_per_pixel})-({colour_range_min_per_pixel}))  ,0),1)
col_scale(z) = (z>{colour_range_max_per_pixel}) ? colors.black : hsb(0.75 * col_scale_z(z), 1, 1)
    
set fontsize 1.1
set nokey

set multiplot

set xlabel "Input {x_label}"
set xrange [{x_range}]
set ylabel "Input {y_label}"
set yrange [{y_range}]
    
set axis y left ; unset xtics ; unset mxtics
plot "{data_filename}" title "SNR needed to achieve accuracy of {target_accuracy} {unit} in {colour_by_label}" \
     with dots colour col_scale($3) ps 8

unset label
set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y y2 right
set ylabel "SNR/\AA (at 6000\AA) needed to achieve accuracy of {target_accuracy} {unit} in {colour_by_label}"
set yrange [{colour_range_min_per_pixel}:{colour_range_max_per_pixel}]
set y2label "SNR/pixel (at 6000\AA)"
set y2range [{colour_range_min_per_a}:{colour_range_max_per_a}]
set c1range [{colour_range_min_per_pixel}:{colour_range_max_per_pixel}] norenormalise
set width {colour_bar_width}
set size ratio 1 / 0.05
set colormap col_scale(c1)
set nocolkey
set sample grid 2x200
set origin {colour_bar_x_pos}, 0
plot y with colourmap
                  
                  """.format(colour_range_min_per_pixel=args.colour_range_min,
                             colour_range_max_per_pixel=args.colour_range_max,
                             colour_range_min_per_a=snr_converter.per_pixel(args.colour_range_min).per_a(),
                             colour_range_max_per_a=snr_converter.per_pixel(args.colour_range_max).per_a(),
                             x_label=label_list[0]["latex"], x_range=label_list[0]["range"],
                             y_label=label_list[1]["latex"], y_range=label_list[1]["range"],
                             data_filename=filename,
                             target_accuracy=args.target_accuracy, unit=args.accuracy_unit,
                             colour_by_label=label_list[2]["latex"],
                             colour_bar_width=plotter.width * plotter.aspect * 0.05,
                             colour_bar_x_pos=plotter.width + 1
                             ))

# Clean up plotter
del plotter
