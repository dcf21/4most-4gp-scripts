#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take some SpectrumLibraries and make a scatter plot of the stellar parameters within them.
"""

import os
import re
import argparse

from lib_multiplotter import make_multiplot

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
parser.add_argument('--binwidth', action="append", dest='binwidth',
                    help="Widths of bins to use in histogram.")
parser.add_argument('--output', default="/tmp/label_values", dest='output',
                    help="Filename to write output plot to.")
args = parser.parse_args()

# If no titles are supplied, default to the names of the libraries
if (args.library_titles is None) or (len(args.library_titles) == 0):
    args.library_titles = [re.sub("_", "\\_", i) for i in args.libraries]

# If no colours are supplied for libraries, default to Pyxplot's sequence of colours
if (args.library_colours is None) or (len(args.library_colours) == 0):
    args.library_colours = [str(i+1) for i in range(len(args.libraries))]

# If no using items specified, assume a sensible default
if (args.using is None) or (len(args.using) == 0):
    args.using = ["$1"]

# If no bin widths specified, make up some values
if (args.binwidth is None) or (len(args.binwidth) == 0):
    args.binwidth = [(25 if item.startswith("Teff") else 0.025) for item in args.labels]

# Check that we have a title for each spectrum library we're plotting
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

# Create pyxplot script to produce each histogram in turn
eps_list = []
pyxplot_input = ""
for counter, using_expression in enumerate(args.using):
    width = 20
    aspect = 1 / 1.618034  # Golden ratio

    stub = "{0}_{1}".format(args.output, counter)

    pyxplot_input += """
    
set nodisplay
set width {0}
set size ratio {1}
set key top left

set xlabel "{2}"
set xrange [{3}]
set ylabel "Stars per unit {2}"

set binwidth {4}
    
    """.format(width, aspect,
               args.label_axis_latex[counter], label_list[counter]["range"],
               args.binwidth[counter]
               )

    for index in range(len(args.libraries)):
        pyxplot_input += """
        
histogram h{0:06d}_{1:03d}() "/tmp/tg{0:06d}.dat" using {2}
    
    """.format(index, counter, using_expression)

    plot_items = []
    for index in range(len(args.libraries)):
        plot_items.append(""" h{0:06d}_{1:03d}(x) title "{2}" with histeps colour {3} """.
                          format(index, counter, args.library_titles[index], args.library_colours[index]))
    pyxplot_input += "plot " + ", ".join(plot_items)

    pyxplot_input += """
    
set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh
    
    """.format(stub)

    eps_list.append("{0}.eps".format(stub))

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()

# Make multiplot
make_multiplot(eps_files=eps_list,
               output_filename="{0}_multiplot".format(args.output),
               aspect=5.5 / 8
               )
