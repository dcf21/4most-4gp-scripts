#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take an output file from the Cannon, and produce a scatter plot of the offset in each label, as a function of the
uncertainty that the Cannon quotes.
"""

import os
import argparse
import json
import numpy as np
from label_tabulator import tabulate_labels

from lib_multiplotter import make_multiplot

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cannon-output',
                    required=True,
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--output-stub', default="/tmp/cannon_uncertainty_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Fetch title for this Cannon run
cannon_output = json.loads(open(args.cannon).read())
description = cannon_output['description']

# Convert SNR/pixel to SNR/A at 6000A
raster = np.array(cannon_output['wavelength_raster'])
raster_diff = np.diff(raster[raster > 6000])
pixels_per_angstrom = 1.0 / raster_diff[0]

# Look up list of labels the Cannon was fitting
label_names = cannon_output['labels']
label_count = len(label_names)

# Create data files listing parameter values
snr_list = tabulate_labels(args.output_stub, label_names, args.cannon)

# Create pyxplot script to produce this plot
width = 20
aspect = 1 / 1.618034  # Golden ratio
pyxplot_input = """

col_scale(z) = hsb(0.75 * z, 1, 1)

"""

eps_list = []
for index, label in enumerate(label_names):
    pyxplot_input += """
    
set nodisplay
set width {0}
set size ratio {1}
set term dpi 200
set key bottom left

set xlabel "Cannon estimated uncertainty in {2}"
# set xrange [0:{3}]
set ylabel "$\Delta$ {2}"
set yrange [-{3}:{3}]

set textvalign top
set label 1 "\\parbox{{{0}cm}}{{{4} \\newline {{\\bf {2} }} }}" at page 0.5, page {5}

""".format(width, aspect, label,
           1000 if label=="Teff" else 2,
           description,
           width * aspect - 0.3
           )

    plot_items = []
    for index2, snr in enumerate(snr_list):
        stub = "{0}_{1:03d}_{2:03d}".format(snr["filename"], index, index2)

        plot_items.append("""
        "{0}" using {1}:(${2}-${3}) title "SNR {4:.1f}" with dots colour col_scale({5}) ps 5
        """.format(
            snr["filename"],
            2*label_count + index + 1,
            index + 1,
            label_count + index + 1,
            snr["snr"] * np.sqrt(pixels_per_angstrom),
            index2 / float(len(snr_list)-1)
        )
        )

    pyxplot_input += """
    
set output "{0}.png"
plot {1}

""".format(snr["filename"], ", ".join([i.strip() for i in plot_items]))

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
               output_filename="{0}_multiplot".format(args.output_stub),
               aspect=6. / 8
               )
