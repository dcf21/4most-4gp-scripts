#!../../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python scatter_plot.py>, but <./scatter_plot.py> will not work.

"""
Take some SpectrumLibraries and make a scatter plot of the stellar parameters within them.
"""

import os
import re
import argparse

from lib.pyxplot_driver import PyxplotDriver
from label_tabulator import tabulate_labels

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, action="append", dest='libraries',
                    help="Library of spectra we should output stellar labels for.")
parser.add_argument('--library-title', action="append", dest='library_titles',
                    help="Short title to give library of spectra.")
parser.add_argument('--library-colour', action="append", dest='library_colours',
                    help="Colour with which to plot a library of spectra.")
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should output values for.")
parser.add_argument('--label-axis-latex', required=True, action="append", dest='label_axis_latex',
                    help="Labels we should output values for.")
parser.add_argument('--using', default="1:2", dest='using',
                    help="Pyxplot using statement.")
parser.add_argument('--output', default="/tmp/label_values", dest='output',
                    help="Filename to write output plot to.")
args = parser.parse_args()

# Create output directory
output_figure_stem = os.path.split(args.output)[0]
os.system("mkdir -p {}".format(output_figure_stem))

# If no titles are supplied, default to the names of the libraries
if (args.library_titles is None) or (len(args.library_titles) == 0):
    args.library_titles = [re.sub("_", "\\_", i) for i in args.libraries]

# If no colours are supplied for libraries, default to Pyxplot's sequence of colours
if (args.library_colours is None) or (len(args.library_colours) == 0):
    args.library_colours = [str(i + 1) for i in range(len(args.libraries))]

# Check that we have a title for each spectrum library we're plotting
assert len(args.library_titles) == len(args.libraries), "Need a title for each library we are plotting"
assert len(args.library_colours) == len(args.libraries), "Need a colour for each library we are plotting"

# Create data files listing the stellar parameters in each library we have been passed
assert len(args.labels) >= 2, "A scatter plot needs at least two labels to plot -- one on each axis."

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
                    output_file="{output}_{index}.dat".format(output=args.output, index=index)
                    )

# Create pyxplot script to produce this plot
plotter = PyxplotDriver()

plotter.make_plot(output_filename=args.output,
                  pyxplot_script="""
                  
set key top left

set xlabel "{x_label}"
set xrange [{x_range}]
set ylabel "{y_label}"
set yrange [{y_range}]

plot {plot_items}
                  
                  """.format(x_label=args.label_axis_latex[0], x_range=label_list[0]["range"],
                             y_label=args.label_axis_latex[1], y_range=label_list[1]["range"],
                             plot_items=", ".join(["""
"{output}_{index}.dat" title "{title}" using {using} with dots colour {colour} ps 8
                             """.format(output=args.output,
                                        index=index,
                                        using=args.using,
                                        title=title,
                                        colour=colour
                                        ).strip()
                                                   for index, (title, colour) in enumerate(zip(args.libraries,
                                                                                               args.library_titles,
                                                                                               args.library_colours))
                                                   ])
                             )
                  )

# Clean up plotter
del plotter
