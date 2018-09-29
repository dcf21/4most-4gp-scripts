#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python internal_model_one_wavelength.py>, but <./internal_model_one_wavelength.py> will not work.

"""
Take an output file from the Cannon, and plot the Cannon's predictive model of how the flux at a particular wavelength
varies with one of the variables.
"""

import argparse
import gzip
import json
import os
import re
from operator import itemgetter
from os import path as os_path

import numpy as np
from fourgp_cannon import CannonInstance_2018_01_09
from fourgp_speclib import SpectrumLibrarySqlite
from lib.pyxplot_driver import PyxplotDriver


def dict_merge(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--wavelength', required=True, dest='wavelength', type=float,
                    help="The wavelength for which we should plot the Cannon's internal model.")
parser.add_argument('--label', required=True, dest='label',
                    help="The label we should vary.")
parser.add_argument('--label-axis-latex', required=True, dest='label_axis_latex',
                    help="Title for this variable that we should put on the horizontal axis of the plot.")
parser.add_argument('--fixed-label', required=True, action="append", dest='fixed_label',
                    help="A fixed value for each of the labels we're not varying.")
parser.add_argument('--cannon-output',
                    required=True,
                    dest='cannon',
                    help="Filename of the JSON file containing the label values estimated by the Cannon, without "
                         "the <.summary.json.gz> suffix.")
parser.add_argument('--output', default="/tmp/cannon_model_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

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
workspace = os_path.join(our_path, "../../../../workspace")

# Create directory to store output files in
os.system("mkdir -p {}".format(args.output_stub))

# Fetch title for this Cannon run
cannon_output = json.loads(gzip.open(args.cannon + ".summary.json.gz").read())
description = cannon_output['description']

# Open spectrum library we originally trained the Cannon on
training_spectra_info = SpectrumLibrarySqlite.open_and_search(
    library_spec=cannon_output["train_library"],
    workspace=workspace,
    extra_constraints={"continuum_normalised": 1}
)

training_library, training_library_items = [training_spectra_info[i] for i in ("library", "items")]

# Load training set
training_library_ids = [i["specId"] for i in training_library_items]
training_spectra = training_library.open(ids=training_library_ids)

# Recreate a Cannon instance, using the saved state
censoring_masks = cannon_output["censoring_mask"]
if censoring_masks is not None:
    for key, value in censoring_masks.items():
        censoring_masks[key] = np.asarray(value)

model = CannonInstance_2018_01_09(training_set=training_spectra,
                                  load_from_file=args.cannon + ".cannon",
                                  label_names=cannon_output["labels"],
                                  censors=censoring_masks,
                                  threads=None
                                  )

# Loop over stars in SpectrumLibrary extracting flux at requested wavelength
raster_index = (np.abs(training_spectra.wavelengths - args.wavelength)).argmin()
value_min = np.inf
value_max = -np.inf

stars = []
for spectrum_number in range(len(training_spectra)):
    metadata = training_spectra.get_metadata(spectrum_number)

    # Check whether this spectra meets the label constraints for this plot
    accept_spectrum = True
    for key in label_constraints:
        if ((key not in metadata) or
                (metadata[key] < label_constraints[key][0]) or
                (metadata[key] > label_constraints[key][1])):
            accept_spectrum = False
    if not accept_spectrum:
        continue

    spectrum = training_spectra.extract_item(spectrum_number)
    value = metadata[args.label]

    if value < value_min:
        value_min = value
    if value > value_max:
        value_max = value

    # Extract name and value of parameter we're varying
    stars.append({
        "name": metadata["Starname"],
        "flux": spectrum.values[raster_index],
        "flux_error": spectrum.value_errors[raster_index],
        "value": value
    })
stars.sort(key=itemgetter("value"))

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
with open("{}/internal_model_one_wavelength.dat".format(args.output_stub), "w") as f:
    for datum in stars:
        f.write("{} {} {}\n".format(datum["value"], datum["flux"], datum["flux_error"]))
    f.write("\n\n\n\n")

    for datum in cannon_predictions:
        f.write("{} {} {}\n".format(datum["value"], datum["flux"], datum["flux_error"]))

# Make list of items we're going to plot
plot_items = []
plot_items.append("""
"{0}/internal_model_one_wavelength.dat" index 0 title "4FS output" with p pt 1 """.
                  format(args.output_stub).strip())
index_counter = 1

plot_items.append("""
"{0}/internal_model_one_wavelength.dat" index {1} title "Cannon internal model" with line color red lw 2 """.
                  format(args.output_stub, index_counter).strip())

# Create pyxplot script to produce this plot
plotter = PyxplotDriver()

plotter.make_plot(output_filename="{}/internal_model_one_wavelength".format(args.output_stub),
                  data_files=["{}/internal_model_one_wavelength.dat".format(args.output_stub)],
                  caption=description,
                  pyxplot_script="""

set numerics errors quiet
set key below
set linewidth 0.4

set xlabel "{x_label}"
set xrange [{x_min}:{x_max}]
set ylabel "Continuum-normalised flux at {wavelength:.1f} A"
set yrange [0.8:1.02]

plot {plot_items}

""".format(x_label=args.label_axis_latex, x_min=value_min, x_max=value_max,
           wavelength=args.wavelength,
           plot_items=", ".join(plot_items)
           )
                  )

# Clean up plotter
del plotter
