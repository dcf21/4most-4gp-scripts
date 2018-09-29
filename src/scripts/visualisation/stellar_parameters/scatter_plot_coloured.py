#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python scatter_plot_coloured.py>, but <./scatter_plot_coloured.py> will not work.

"""
Take some SpectrumLibraries and make a coloured scatter plot of the stellar parameters within them.
"""

import argparse
import os
import re

from label_tabulator import tabulate_labels
from lib.pyxplot_driver import PyxplotDriver

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, action="append", dest='libraries',
                    help="Library of spectra we should plot stellar parameters from.")
parser.add_argument('--library-title', action="append", dest='library_titles',
                    help="Short title to give to library of spectra in plot legend.")
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should put on the axes of the scatter plot (can supply more than two and supply "
                         "a USING statement to combine them in an algebraic expression).")
parser.add_argument('--label-axis-latex', required=True, action="append", dest='label_axis_latex',
                    help="Titles we should put on the two axes of the scatter plot.")
parser.add_argument('--using', default="1:2", dest='using',
                    help="Pyxplot using statement we should use to get the x and y values for each point in "
                         "scatter plot.")
parser.add_argument('--using-colour', default="$3", dest='colour_expression',
                    help="Pyxplot using statement we should use to derive the colour of each point.")
parser.add_argument('--colour-range-min', required=True, dest='colour_range_min', type=float,
                    help="The range of parameter values to use in colouring points.")
parser.add_argument('--colour-range-max', required=True, dest='colour_range_max', type=float,
                    help="The range of parameter values to use in colouring points.")
parser.add_argument('--output', default="/tmp/scatter_plot_coloured", dest='output_stem',
                    help="Directory to write plot to.")
args = parser.parse_args()

# Create output directory
os.system("mkdir -p {}".format(args.output_stem))

# If no titles are supplied, default to the names of the libraries
if (args.library_titles is None) or (len(args.library_titles) == 0):
    args.library_titles = [re.sub("_", "\\_", i) for i in args.libraries]

# Check that we have a title for each spectrum library we're plotting
assert len(args.library_titles) == len(args.libraries), "Need a title for each library we are plotting"

# Create data files listing the stellar parameters in each library we have been passed
assert len(args.labels) >= 3, \
    "A scatter plot needs at least three labels to plot -- one on each axis, plus one to colour."

label_list = []
for item in args.labels:
    test = re.match("(.*){(.*:.*)}", item)
    assert test is not None, "Label names should take the form <name{:2}>, with range to plot in {}."
    label_list.append({
        "name": test.group(1),
        "range": test.group(2)
    })

for index, library in enumerate(args.libraries):
    tabulate_labels(library_list=[library],
                    label_list=[item['name'] for item in label_list],
                    output_file="{output}/{index}.dat".format(output=args.output_stem, index=index)
                    )

# Create pyxplot script to produce this plot
plotter = PyxplotDriver()

for mode in ["colour", "mono"]:
    plotter.make_plot(output_filename="{}/{}".format(args.output_stem, mode),
                      data_files=["{output}/{index}.dat".format(output=args.output_stem, index=index)
                                  for index in range(len(args.libraries))],
                      caption=r"\bf {}".format(r" \newline ".join(args.library_titles)),
                      pyxplot_script="""

set nokey
set multiplot

set xlabel "{x_label}"
set xrange [{x_range}]
set ylabel "{y_label}"
set yrange [{y_range}]

col_scale_z(z) = min(max(  (z-({colour_range_min})) / (({colour_range_max})-({colour_range_min}))  ,0),1)
col_scale(z) = hsb(0.75 * col_scale_z(z), 1, 1)

plot {plot_items}

{make_colour_scale}

                      """.format(x_label=args.label_axis_latex[0], x_range=label_list[0]["range"],
                                 y_label=args.label_axis_latex[1], y_range=label_list[1]["range"],
                                 colour_range_min=args.colour_range_min, colour_range_max=args.colour_range_max,
                                 plot_items=", ".join(["""
"{output}/{index}.dat" title "{title}" using {using} with dots colour {colour} ps 8
                                 """.format(output=args.output_stem,
                                            index=index,
                                            title=title,
                                            using=args.using,
                                            colour=("col_scale({colour_exp})".format(colour_exp=args.colour_expression)
                                                    if mode == "colour"
                                                    else "black")
                                            ).strip()
                                                       for index, (library, title) in enumerate(zip(args.libraries,
                                                                                                    args.library_titles))
                                                       ]),
                                 make_colour_scale=("""
set noxlabel
unset label
set xrange [0:1]
set noxtics ; set nomxtics
set axis y right
set ylabel "{label_latex}"
set yrange [{colour_range_min}:{colour_range_max}]
set c1range [{colour_range_min}:{colour_range_max}] norenormalise
set width {colour_bar_width}
set size ratio 1 / 0.05
set colormap col_scale(c1)
set nocolkey
set sample grid 2x200
set origin {colour_bar_x_pos}, 0
plot y with colourmap
                                            """.format(label_latex=args.label_axis_latex[2],
                                                       colour_range_min=args.colour_range_min,
                                                       colour_range_max=args.colour_range_max,
                                                       colour_bar_width=plotter.width * plotter.aspect * 0.05,
                                                       colour_bar_x_pos=plotter.width + 1)
                                                    if mode == "colour"
                                                    else "")
                                 )
                      )

# Clean up plotter
del plotter
