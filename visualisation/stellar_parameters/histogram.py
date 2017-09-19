#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take some SpectrumLibraries and make a scatter plot of the stellar parameters within it.
"""

import os
import re
import argparse

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, action="append", dest='libraries',
                    help="Library of spectra we should output stellar labels for.")
parser.add_argument('--library-title', required=True, action="append", dest='library_titles',
                    help="Short title to give library of spectra.")
parser.add_argument('--library-colour', required=True, action="append", dest='library_colours',
                    help="Colour with which to plot a library of spectra.")
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should output histogram for.")
parser.add_argument('--label-axis-latex', required=True, dest='label_axis_latex',
                    help="Labels we should output histogram for.")
parser.add_argument('--using', default="1:2", dest='using',
                    help="Pyxplot using statement.")
parser.add_argument('--binwidth', default="0.05", dest='binwidth',
                    help="Widths of bins to use in histogram.")
parser.add_argument('--output', default="/tmp/label_values", dest='output',
                    help="Filename to write output plot to.")
args = parser.parse_args()

assert len(args.library_titles) == len(args.libraries), "Need a title for each library we are plotting"
assert len(args.library_colours) == len(args.libraries), "Need a colour for each library we are plotting"

# Create data files listing the stellar parameters in each library we have been passed
assert len(args.labels) >= 1, "A histogram needs at least one label to plot."

label_list = []
label_command_line = ""
for item in args.labels:
    test = re.match("(.*){(.*:.*)}", item)
    assert test is not None, "Label names should take the form <name[:2]>, with range to plot in []."
    label_list.append({
        "name": test.group(1),
        "range": test.group(2)
    })
    label_command_line += " --label \"{}\" ".format(test.group(1))

for index, library in enumerate(args.libraries):
    os.system("python label_tabulator.py --library {0} {1} --output-file /tmp/tg{2:06d}.dat".
              format(library, label_command_line, index))

# Create pyxplot script to produce this plot
pyxplot_input = """
set nodisplay
set width 14
set key top left

set xlabel "{}"
set xrange [{}]
set ylabel "Stars per unit $x$"

set binwidth {}
""".format(args.label_axis_latex, label_list[0]["range"], args.binwidth)

for index in range(len(args.libraries)):
    pyxplot_input += """
histogram h{0:06d}() "/tmp/tg{0:06d}.dat" using {1}
""".format(index, args.using)

plot_items = []
for index in range(len(args.libraries)):
    plot_items.append(""" h{0:06d}(x) title "{1}" with histeps colour {2} """.
                      format(index, args.library_titles[index], args.library_colours[index]))
pyxplot_input += "plot " + ", ".join(plot_items)

pyxplot_input += """
set term eps ; set output "{0}.eps" ; set display ; refresh
set term png ; set output "{0}.png" ; set display ; refresh
""".format(args.output)

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
