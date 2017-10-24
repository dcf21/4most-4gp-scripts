#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take some SpectrumLibraries and make a coloured scatter plot of the stellar parameters within them.
"""

import os
import re
import argparse

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
parser.add_argument('--output', default="/tmp/label_values", dest='output',
                    help="Filename to write output plot to.")
args = parser.parse_args()

# If no titles are supplied, default to the names of the libraries
if (args.library_titles is None) or (len(args.library_titles) == 0):
    args.library_titles = [re.sub("_", "\\_", i) for i in args.libraries]

# Check that we have a title for each spectrum library we're plotting
assert len(args.library_titles) == len(args.libraries), "Need a title for each library we are plotting"

# Create data files listing the stellar parameters in each library we have been passed
assert len(args.labels) >= 3, \
    "A scatter plot needs at least three labels to plot -- one on each axis, plus one to colour."

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

#

# Create pyxplot script to produce this plot
width = 20
aspect = 1 / 1.618034  # Golden ratio
pyxplot_input = """

set nodisplay
set width {0}
set size ratio {1}
set nokey

set multiplot

set xlabel "{2}"
set xrange [{3}]
set ylabel "{4}"
set yrange [{5}]

set textvalign top
set label 1 "\\parbox{{{0}cm}}{{ {6} }}" at page 0.5, page {7}

""".format(width, aspect,
           args.label_axis_latex[0], label_list[0]["range"], args.label_axis_latex[1], label_list[1]["range"],
           " \\newline ".join(args.library_titles),
           width*aspect-0.3
           )

pyxplot_input += """

col_scale_z(z) = min(max(  (z-({0})) / (({1})-({0}))  ,0),1)

col_scale(z) = hsb(0.75 * col_scale_z(z), 1, 1)

""".format(args.colour_range_min, args.colour_range_max)

plot_items = []
for index in range(len(args.libraries)):
    plot_items.append(""" "/tmp/tg{:06d}.dat" title "{}" using {} with dots colour col_scale({}) ps 5 """.
                      format(index, args.library_titles[index], args.using, args.colour_expression))
pyxplot_input += "plot " + ", ".join(plot_items)

pyxplot_input += """

set noxlabel
unset label
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

set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh

""".format(args.output)

# Create mono version

pyxplot_input = """

set nodisplay
clear
set width {0}
set size ratio {1}
set nokey
set multiplot

set xlabel "{2}"
set xrange [{3}]
set ylabel "{4}"
set yrange [{5}]

set textvalign top
set label 1 "\\parbox{{{0}cm}}{{ {6} }}" at page 0.5, page {7}

""".format(width, aspect,
           args.label_axis_latex[0], label_list[0]["range"], args.label_axis_latex[1], label_list[1]["range"],
           " \\newline ".join(args.library_titles),
           width*aspect-0.3
           )

plot_items = []
for index in range(len(args.libraries)):
    plot_items.append(""" "/tmp/tg{:06d}.dat" title "{}" using {} with dots colour black ps 5 """.
                      format(index, args.library_titles[index], args.using, args.colour_expression))
pyxplot_input += "plot " + ", ".join(plot_items)

pyxplot_input += """

set term eps ; set output '{0}_mono.eps' ; set display ; refresh
set term png ; set output '{0}_mono.png' ; set display ; refresh
set term pdf ; set output '{0}_mono.pdf' ; set display ; refresh

""".format(args.output)

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
