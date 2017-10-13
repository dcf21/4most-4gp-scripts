#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take some SpectrumLibraries and make a scatter plot of the stellar parameters within them.
"""

import os
import re
import argparse

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

# If no titles are supplied, default to the names of the libraries
if (args.library_titles is None) or (len(args.library_titles) == 0):
    args.library_titles = [re.sub("_", "\\_", i) for i in args.libraries]

# If no colours are supplied for libraries, default to Pyxplot's sequence of colours
if (args.library_colours is None) or (len(args.library_colours) == 0):
    args.library_colours = [str(i+1) for i in range(len(args.libraries))]

# Check that we have a title for each spectrum library we're plotting
assert len(args.library_titles) == len(args.libraries), "Need a title for each library we are plotting"
assert len(args.library_colours) == len(args.libraries), "Need a colour for each library we are plotting"

# Create data files listing the stellar parameters in each library we have been passed
assert len(args.labels) >= 2, "A scatter plot needs at least two labels to plot -- one on each axis."

label_list = []
label_command_line = ""
for item in args.labels:
    test = re.match("(.*){(.*:.*)}", item)
    assert test is not None, "Label names should take the form <name{:2}>, with range to plot in {}."
    label_list.append({
        "name": test.group(1),
        "range": test.group(2)
    })
    label_command_line += " --label \"{}\" ".format(test.group(1))

for index, library in enumerate(args.libraries):
    os.system("python label_tabulator.py --library {0} {1} --output-file /tmp/tg{2:06d}.dat".
              format(library, label_command_line, index))

# Create pyxplot script to produce this plot
width = 20
aspect = 1 / 1.618034  # Golden ratio

pyxplot_input = """

set nodisplay
set width {0}
set size ratio {1}
set key top left

set xlabel "{2}"
set xrange [{3}]
set ylabel "{4}"
set yrange [{5}]

""".format(width, aspect,
           args.label_axis_latex[0], label_list[0]["range"],
           args.label_axis_latex[1], label_list[1]["range"]
           )

plot_items = []
for index in range(len(args.libraries)):
    plot_items.append(""" "/tmp/tg{:06d}.dat" title "{}" using {} with dots colour {} ps 8 """.
                      format(index, args.library_titles[index], args.using, args.library_colours[index]))
pyxplot_input += "plot " + ", ".join(plot_items)

pyxplot_input += """

set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh

""".format(args.output)

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
