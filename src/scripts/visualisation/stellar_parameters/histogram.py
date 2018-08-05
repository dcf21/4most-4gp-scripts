#!../../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python histogram.py>, but <./histogram.py> will not work.

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
                    help="Labels we should output histogram for.")
parser.add_argument('--label-axis-latex', action="append", required=True, dest='label_axis_latex',
                    help="Labels we should output histogram for.")
parser.add_argument('--using', action="append", dest='using',
                    help="Pyxplot using statement.")
parser.add_argument('--bin-width', action="append", dest='bin_width',
                    help="Widths of bins to use in histogram.")
parser.add_argument('--output', default="/tmp/label_values", dest='output_stem',
                    help="Directory to write plot to.")
args = parser.parse_args()

# Create output directory
os.system("mkdir -p {}".format(args.output_stem))

# If no titles are supplied, default to the names of the libraries
if (args.library_titles is None) or (len(args.library_titles) == 0):
    args.library_titles = [re.sub("_", "\\_", i) for i in args.libraries]

# If no colours are supplied for libraries, default to Pyxplot's sequence of colours
if (args.library_colours is None) or (len(args.library_colours) == 0):
    args.library_colours = [str(i + 1) for i in range(len(args.libraries))]

# If no using items specified, assume a sensible default
if (args.using is None) or (len(args.using) == 0):
    args.using = ["$1"]

# If no bin widths specified, make up some values
if (args.bin_width is None) or (len(args.bin_width) == 0):
    args.bin_width = [(25 if item.startswith("Teff") else 0.025) for item in args.labels]

# Check that we have a title for each spectrum library we're plotting
assert len(args.library_titles) == len(args.libraries), "Need a title for each library we are plotting"
assert len(args.library_colours) == len(args.libraries), "Need a colour for each library we are plotting"

# Create data files listing the stellar parameters in each library we have been passed
assert len(args.labels) >= 1, "A histogram needs at least one label to plot."

label_list = []
for item in args.labels:
    test = re.match("(.*){(.*:.*)}", item)
    assert test is not None, "Label names should take the form <name[:2]>, with range to plot in []."
    label_list.append({
        "name": test.group(1),
        "range": test.group(2)
    })

for index, library in enumerate(args.libraries):
    tabulate_labels(library_list=[library],
                    label_list=[item['name'] for item in label_list],
                    output_file="{output}/{index}.dat".format(output=args.output_stem, index=index)
                    )

# Create pyxplot script to produce each histogram in turn
plotter = PyxplotDriver(multiplot_filename="{0}/multiplot".format(args.output_stem),
                        multiplot_aspect=5.5 / 8)

for counter, using_expression in enumerate(args.using):
    plotter.make_plot(output_filename="{output}/{counter}".format(output=args.output_stem, counter=counter),
                      data_files=["{output}/{index}.dat".format(output=args.output_stem, index=index)
                                  for index in range(len(args.libraries))],
                      pyxplot_script="""
    
set nokey # key top right

set xlabel "{x_label}"
set xrange [{x_range}]
set ylabel "Stars per unit {x_label}"

set binwidth {bin_width}

{make_histograms}

plot {plot_items}

    """.format(x_label=args.label_axis_latex[counter],
               x_range=label_list[counter]["range"],
               bin_width=args.bin_width[counter],
               make_histograms="\n".join(["""
histogram h{index:06d}_{counter:03d}() "{output}/{index}.dat" using {using}
               """.format(index=index,
                          counter=counter,
                          output=args.output_stem,
                          using=using_expression)
                                          for index, library in enumerate(args.libraries)
                                          ]),
               plot_items=", ".join(["""
h{index:06d}_{counter:03d}(x) title "{title}" with histeps colour {colour}
               """.format(index=index,
                          counter=counter,
                          title=title,
                          colour=colour
                          ).strip()
                                     for index, (library, title, colour) in enumerate(zip(args.libraries,
                                                                                          args.library_titles,
                                                                                          args.library_colours))
                                     ])
               )
                      )

# Clean up plotter
del plotter
