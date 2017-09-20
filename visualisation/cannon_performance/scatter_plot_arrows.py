#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take a SpectrumLibrary containing some spectra which the Cannon has tried to fit, and a scatter plot with arrows
connecting the library parameter values to those estimated by the Cannon.
"""

import os
import argparse
import re
from label_tabulator import tabulate_labels

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library', required=True, dest='library',
                    help="Library of spectra we should output stellar labels for.")
parser.add_argument('--label', required=True, action="append", dest='labels',
                    help="Labels we should output values for.")
parser.add_argument('--cannon_output',
                    required=True,
                    default="",
                    dest='cannon',
                    help="Cannon output file.")
parser.add_argument('--output-stub', default="/tmp/cannon_estimates_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Create data files listing the stellar parameters in each library we have been passed
assert len(args.labels) >= 2, "A scatter plot needs at least two labels to plot -- one on each axis."

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

# Create data files listing parameter values
snr_list = tabulate_labels(args.output_stub, args.library, label_names, args.cannon)

pyxplot_input = """
set term png dpi 200
set width 25
set key top left
set linewidth 0.4

set xlabel "{}"
set xrange [{}]
set ylabel "{}"
set yrange [{}]
""".format(args.label_axis_latex[0], label_list[0]["range"], args.label_axis_latex[1], label_list[1]["range"])

for snr in snr_list:
    pyxplot_input += """
set nodisplay
set output "{0}.png"
plot "{0}" title "Cannon output -$>$ Synthesised values. SNR {1}." with arrows c red using 3:4:1:2
set term eps ; set output "{0}.eps" ; set display ; refresh
set term png ; set output "{0}.png" ; set display ; refresh
""".format(snr["filename"], snr["snr"])

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()