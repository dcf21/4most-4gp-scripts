#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take an output file from the Cannon, and plot the Cannon's predictive model of how the flux at a particular wavelength
varies with one of the variables.
"""

import os
from os import path as os_path
import argparse
import re
import json
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import CannonInstance

from lib_multiplotter import make_multiplot

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--wavelength', required=True, dest='wavelength', type=float,
                    help="The wavelength for which we should plot the Cannon's internal model.")
parser.add_argument('--library', required=True, dest='library',
                    help="Spectrum library we should plot over Cannon's internal model.")
parser.add_argument('--label', required=True, dest='labels',
                    help="Label we should vary.")
parser.add_argument('--label-axis-latex', required=True, dest='label_axis_latex',
                    help="Title for this variable that we should put on the horizontal axis of the plot.")
parser.add_argument('--fixed-label', required=True, action="append", dest='fixed_label',
                    help="A fixed value for each of the labels we're not varying.")
parser.add_argument('--cannon-output',
                    required=True,
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--output-stub', default="/tmp/cannon_model_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Fixed labels are supplied in the form <name=value>
label_constraints = {}
for item in args.fixed_label:
    test = re.match("(.*)=(.*)", item)
    assert test is not None, "Fixed labels should be specified in the form <name=value>."
    value = test.group(2)
    try:
        value = float(value)
    except ValueError:
        pass
    label_constraints[test.group(1)] = value

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "workspace")

# Open Spectrum library
library_path = os_path.join(workspace, args.library)
input_library = SpectrumLibrarySqlite(path=library_path, create=False)
library_items = input_library.search(**label_constraints)

# Fetch title for this Cannon run
cannon_output = json.loads(open(args.cannon+".json").read())
description = cannon_output['description']

# Convert SNR/pixel to SNR/A at 6000A
raster = np.array(cannon_output['wavelength_raster'])
raster_diff = np.diff(raster[raster > 6000])
pixels_per_angstrom = 1.0 / raster_diff[0]

# Recreate a Cannon instance, using the saved state
censoring_masks = cannon_output["censoring_mask"]
if censoring_masks is not None:
    for key, value in censoring_masks.iteritems():
        censoring_masks[key] = np.asarray(value)

model = CannonInstance(training_set=library_items,
                       load_from_file=args.cannon+".cannon",
                       label_names=cannon_output["labels"],
                       censors=censoring_masks,
                       threads=None
                       )

# Loop over stars in SpectrumLibrary extracting flux at requested wavelength
stars = []
raster_index = (np.abs(library_items.wavelengths-args.wavelength)).argmin()
value_min = np.inf
value_max = -np.inf
for spectrum_number in range(len(library_items)):
    metadata = library_items.get_metadata(spectrum_number)
    spectrum = library_items.extract_item(spectrum_number)
    value = metadata[args.label]

    if value<value_min:
        value_min = value
    if value>value_max:
        value_max = value

    # Extract name and value of parameter we're varying
    stars.append({
        "name": metadata["Starname"],
        "flux": spectrum.values[raster_index],
        "flux_error": spectrum.value_errors[raster_index],
        "value": value
    })

# Query Cannon's internal model of this pixel
n_steps = 100
cannon = model._model
raster_index = (np.abs(cannon.dispersion-args.wavelength)).argmin()
cannon_predictions = []
for i in range(n_steps):
    label_values = label_constraints.copy()
    value = value_min + i*(value_max-value_min)
    label_values[args.label] = value
    cannon_predicted_spectrum = cannon.predict(label_values)
    cannon_predictions.append({
        "value": value,
        "flux": cannon_predicted_spectrum[raster_index],
        "flux_errors": cannon.s2[raster_index]
    })

# Write data file for PyXPlot to plot
with open("{}.dat".format(args.output_stub)) as f:
    for datum in stars:
        f.write("{} {} {}\n".format(datum["value"], datum["flux"], datum["flux_error"]))

    f.write("\n\n\n\n")

    for datum in cannon_predictions:
        f.write("{} {} {}\n".format(datum["value"], datum["flux"], datum["flux_error"]))

# Create pyxplot script to produce this plot
width = 25
aspect = 1 / 1.618034  # Golden ratio
pyxplot_input = """

set width {0}
set size ratio {1}
set term dpi 200
set key top left
set linewidth 0.4

set xlabel "{2}"
set xrange [{3}:{4}]
set ylabel "Flux at wavelength of {5:.1f} A"
set yrange [0:1.2]

set label 1 "{6}" at page 0.5, page {7}

""".format(width, aspect,
           args.label_axis_latex, value_min, value_max,
           args.wavelength,
           description, width * aspect - 1.1)

pyxplot_input += """
    
set nodisplay
set output "{0}.png"
plot "{0}.dat" index 0 title "Synthesised spectra" with yerrorbars, \
     "{0}.dat" index 1 title "Cannon internal model" with line color red lw 2
set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh

""".format(args.output_stub)

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
