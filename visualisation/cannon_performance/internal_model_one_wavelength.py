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

from operator import itemgetter

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_cannon import CannonInstance

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--wavelength', required=True, dest='wavelength', type=float,
                    help="The wavelength for which we should plot the Cannon's internal model.")
parser.add_argument('--library', required=True, dest='library',
                    help="Spectrum library we should plot over Cannon's internal model.")
parser.add_argument('--train-library', required=True, dest='train_library',
                    help="Spectrum library that we originally used to train the Cannon. Must match EXACTLY!")
parser.add_argument('--label', required=True, dest='label',
                    help="The label we should vary.")
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


# Helper for opening input SpectrumLibrary(s)
def open_input_libraries(library_spec, extra_constraints):
    test = re.match("([^\[]*)\[(.*)\]$", library_spec)
    constraints = {}
    if test is None:
        library_name = library_spec
    else:
        library_name = test.group(1)
        for constraint in test.group(2).split(","):
            words_1 = constraint.split("=")
            words_2 = constraint.split("<")
            if len(words_1) == 2:
                constraint_name = words_1[0]
                try:
                    constraint_value = float(words_1[1])
                except ValueError:
                    constraint_value = words_1[1]
                constraints[constraint_name] = constraint_value
            elif len(words_2) == 3:
                constraint_name = words_2[1]
                try:
                    constraint_value_a = float(words_2[0])
                    constraint_value_b = float(words_2[2])
                except ValueError:
                    constraint_value_a = words_2[0]
                    constraint_value_b = words_2[2]
                constraints[constraint_name] = (constraint_value_a, constraint_value_b)
            else:
                assert False, "Could not parse constraint <{}>".format(constraint)
    constraints.update(extra_constraints)
    constraints["continuum_normalised"] = 1  # All input spectra must be continuum normalised
    library_path = os_path.join(workspace, library_name)
    input_library = SpectrumLibrarySqlite(path=library_path, create=False)
    library_items = input_library.search(**constraints)
    return {
        "library": input_library,
        "items": library_items
    }


# Fixed labels are supplied in the form <name=value>
label_constraints = {}
label_fixed_values = {}
for item in args.fixed_label:
    test = re.match("(.*)=(.*)", item)
    assert test is not None, "Fixed labels should be specified in the form <name=value>."
    value = test.group(2)
    constraint_range = test.group(2)
    # Convert parameter values to floats wherever possible
    try:
        # Express constraint as a narrow range, to allow wiggle-room for numerical inaccuracy
        value = float(value)
        constraint_range = (value - 1e-3, value + 1e-3)
    except ValueError:
        pass
    label_fixed_values[test.group(1)] = value
    label_constraints[test.group(1)] = constraint_range

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "..", "..", "workspace")

# Open spectrum library we're going to plot
input_library_info = open_input_libraries(args.library, label_constraints)
input_library, library_items = [input_library_info[i] for i in ("library", "items")]
library_ids = [i["specId"] for i in library_items]
library_spectra = input_library.open(ids=library_ids)

# Divide up spectra by SNR, and plot each separately
library_spectra_by_snr = {}
for i in range(len(library_spectra)):
    snr = 0
    metadata = library_spectra.get_metadata(i)
    if "SNR" in metadata:
        snr = metadata["SNR"]
    if snr not in library_spectra_by_snr:
        library_spectra_by_snr[snr] = []
    library_spectra_by_snr[snr].append(i)

# Open spectrum library we originally trained the Cannon on
training_spectra_info = open_input_libraries(args.train_library, {})
training_library, training_library_items = [training_spectra_info[i] for i in ("library", "items")]

# Load training set
training_library_ids = [i["specId"] for i in training_library_items]
training_spectra = training_library.open(ids=training_library_ids)

# Fetch title for this Cannon run
cannon_output = json.loads(open(args.cannon + ".json").read())
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

model = CannonInstance(training_set=training_spectra,
                       load_from_file=args.cannon + ".cannon",
                       label_names=cannon_output["labels"],
                       censors=censoring_masks,
                       threads=None
                       )

# Loop over stars in SpectrumLibrary extracting flux at requested wavelength
stars = {}
raster_index = (np.abs(library_spectra.wavelengths - args.wavelength)).argmin()
value_min = np.inf
value_max = -np.inf
for snr in library_spectra_by_snr.keys():
    stars[snr] = []
    for spectrum_number in library_spectra_by_snr[snr]:
        metadata = library_spectra.get_metadata(spectrum_number)
        spectrum = library_spectra.extract_item(spectrum_number)
        value = metadata[args.label]

        if value < value_min:
            value_min = value
        if value > value_max:
            value_max = value

        # Extract name and value of parameter we're varying
        stars[snr].append({
            "name": metadata["Starname"],
            "flux": spectrum.values[raster_index],
            "flux_error": spectrum.value_errors[raster_index],
            "value": value
        })
    stars[snr].sort(key=itemgetter("value"))

# Query Cannon's internal model of this pixel
n_steps = 100
cannon = model._model
raster_index = (np.abs(cannon.dispersion - args.wavelength)).argmin()
cannon_predictions = []
for i in range(n_steps):
    label_values = label_fixed_values.copy()
    value = value_min + i * (value_max - value_min) / (n_steps - 1.)
    label_values[args.label] = value
    label_vector = np.asarray([label_values[key] for key in cannon_output["labels"]])
    cannon_predicted_spectrum = cannon.predict(label_vector)[0]
    cannon_predictions.append({
        "value": value,
        "flux": cannon_predicted_spectrum[raster_index],
        "flux_error": cannon.s2[raster_index]
    })

# Write data file for PyXPlot to plot
with open("{}.dat".format(args.output_stub), "w") as f:
    for snr in sorted(stars.keys()):
        for datum in stars[snr]:
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
set key below
set linewidth 0.4

set xlabel "{2}"
set xrange [{3}:{4}]
set ylabel "Continuum-normalised flux at {5:.1f} A"
set yrange [0.8:1.02]

set label 1 "{6}" at page 0.5, page {7}
    
set nodisplay
set output "{8}.png"
plot """.format(width, aspect,
                args.label_axis_latex, value_min, value_max,
                args.wavelength,
                description, width * aspect - 1.1,
                args.output_stub)

plot_items = []
index_counter = 0
for snr in sorted(stars.keys()):
    plot_items.append(""" "{0}.dat" index {1} title "4FS output at SNR/pixel {2:.1f}" with p pt 1 """.
                      format(args.output_stub, index_counter, snr))
    index_counter += 1

plot_items.append(""" "{0}.dat" index {1} title "Cannon internal model" with line color red lw 2 """.
                  format(args.output_stub, index_counter))

pyxplot_input += ", ".join(plot_items)

pyxplot_input += """

set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh

""".format(args.output_stub)

# Run pyxplot
p = os.popen("pyxplot", "w")
p.write(pyxplot_input)
p.close()
