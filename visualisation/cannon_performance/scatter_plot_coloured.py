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

from lib.label_information import LabelInformation
from lib.multiplotter import PyxplotDriver

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should plot on the two axes of the scatter plot.")
parser.add_argument('--colour-by-label', required=True, dest='colour_by_label',
                    help="Label we should use to colour code points by the Cannon's offset from library values.")
parser.add_argument('--cannon-output',
                    required=True,
                    default="",
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--output', default="/tmp/cannon_estimates_", dest='output_stub',
                    help="Data file to write output to.")
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

# Fetch title for this Cannon run
if not os.path.exists(args.cannon):
    print "scatter_plot_coloured.py could not proceed: Cannon run <{}> not found".format(args.cannon)
    sys.exit()

cannon_output = json.loads(open(args.cannon).read())
description = cannon_output['description']

# Check that labels exist
for label in label_list:
    if label["name"] not in cannon_output["labels"]:
        print "scatter_plot_coloured.py could not proceed: Label <{}> not present in <{}>".format(label["name"],
                                                                                                  args.cannon)
        sys.exit()

# Create data files listing parameter values
snr_list = tabulate_labels(args.output_stub, [i['name'] for i in label_names], args.cannon)

# Convert SNR/pixel to SNR/A at 6000A
raster = np.array(cannon_output['wavelength_raster'])
raster_diff = np.diff(raster[raster > 6000])
pixels_per_angstrom = 1.0 / raster_diff[0]

# Create pyxplot script to produce this plot
plotter = PyxplotDriver(multiplot_filename="{0}_multiplot".format(args.output_stub),
                        multiplot_aspect=4.8 / 8)

for snr in snr_list:
    plotter.make_plot(output_filename=snr["filename"],
                      caption=r"""
{description} \newline {{\bf {label_latex} }} \newline SNR/\AA={snr_a:.1f} \newline SNR/pixel={snr_pixel:.1f}
                      """.format(description=description,
                                 label_latex=args.label_axis_latex[2],
                                 snr_a=snr["snr"] * np.sqrt(pixels_per_angstrom),
                                 snr_pixel=snr["snr"]
                                 ).strip(),
                      pyxplot_script="""

col_scale_z(z) = min(max(  (z-({colour_range_min})) / (({colour_range_max})-({colour_range_min}))  ,0),1)
col_scale(z) = hsb(0.75 * col_scale_z(z), 1, 1)
    
set nokey
set multiplot

set xlabel "Input {x_label}"
set xrange [{x_range}]
set ylabel "Input {y_label}"
set yrange [{y_range}]

set axis y left ; unset xtics ; unset mxtics
plot "{data_filename}" title "Offset in {label_latex} at SNR {snr_pixel}." with dots colour col_scale($6-$3) ps 8

unset label
set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y right
set ylabel "Offset in {label_latex}"
set yrange [{colour_range_min}:{colour_range_max}]
set c1range [{colour_range_min}:{colour_range_max}] norenormalise
set width {colour_bar_width}
set size ratio 1 / 0.05
set colormap col_scale(c1)
set nocolkey
set sample grid 2x200
set origin {colour_bar_x_pos}, 0
plot y with colourmap

""".format(colour_range_min=label_list[2]["min"],
           colour_range_max=label_list[2]["max"],
           x_label=label_list[0]["latex"], x_range=label_list[0]["range"],
           y_label=label_list[1]["latex"], y_range=label_list[1]["range"],
           data_filename=snr["filename"],
           label_latex=label_list[2]["latex"],
           snr_pixel=snr["snr"],
           colour_bar_width=plotter.width * plotter.aspect * 0.05,
           colour_bar_x_pos=plotter.width + 1
           )
                      )

# Clean up plotter
del plotter
