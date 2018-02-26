#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take an output file from the Cannon, where stars have been run at a range of SNRs and E(B-V) values. Produce a plot
of the exposure time needed to yield various abundances to various precision targets.
"""

import os
from os import path as os_path
import sys
import argparse
import json
import re
import numpy as np

from fourgp_speclib import SpectrumLibrarySqlite

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--abundance-target', action="append", dest='targets',
                    help="Abundances we're trying to recover with a given precision target.")
parser.add_argument('--cannon-output',
                    default="../../output_data/cannon/cannon_reddened_fourteam2_sample_hrs_10label.json",
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--plot-width', default="18", dest='width',
                    help="Width of each plot.")
parser.add_argument('--output-stub', default="/tmp/cannon_estimates_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "..", "workspace")


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


# Read Cannon output
if not os.path.exists(args.cannon):
        print "scatter_plot_snr_required.py could not proceed: Cannon run <{}> not found".format(args.cannon)
        sys.exit()

cannon_output = json.loads(open(args.cannon).read())

# Create a sorted list of all the SNR values we've got
snr_values = [item['SNR'] for item in cannon_output['stars']]
snr_values = sorted(set(snr_values))

# Create a sorted list of all the stars we've got
star_names = [item['Starname'] for item in cannon_output['stars']]
star_names = sorted(set(star_names))

# Create a sorted list of all the E(B-V) values we've got
ebv_values = [item['e_bv'] for item in cannon_output['stars']]
ebv_values = sorted(set(ebv_values))

# Work out multiplication factor to convert SNR/pixel to SNR/A
raster = np.array(cannon_output['wavelength_raster'])
raster_diff = np.diff(raster[raster > 6000])
pixels_per_angstrom = 1.0 / raster_diff[0]

# Open original spectrum library, so we can extract exposure time metadata
input_library_info = open_input_libraries(cannon_output['test_library'], {})
input_library, library_items = [input_library_info[i] for i in ("library", "items")]

# Loop over stars, reorganising data by star name and E(B-V)
data = {}
for star in cannon_output['stars']:
    object_name = star['Starname']
    if object_name not in data:
        data[object_name] = {}
    e_bv = star['e_bv']
    if e_bv not in data[object_name]:
        data[object_name][e_bv] = {}
    uid = star['uid']
    spectra_list = input_library.search(uid=uid, continuum_normalised=1)
    assert len(spectra_list) == 1, "Multiple spectra with the same UID"
    spectra_ids = [i["specId"] for i in spectra_list]
    spectra_array = input_library.open(ids=spectra_ids)
    metadata = spectra_array.get_metadata(0)
    exposure_time = metadata['exposure']
    if np.isfinite(exposure_time):
        data[object_name][e_bv][exposure_time] = star

# Loop over stars, plotting each in turn
exposure = {}  # exposure[star_name][target][E_BV] = exposure time
for star_name in star_names:
    exposure[star_name] = {}

    # Loop over all of the performance targets we're plotting
    for j, target in enumerate(args.targets):
        exposure[star_name][j] = {}
        # Extract target element and precision from string of the form "[Fe/H]<0.1" or "[Mg/Fe]<0.2"
        test1 = re.match(r"\[(.*)/H\]<(.*)", target)
        test2 = re.match(r"\[(.*)/Fe\]<(.*)", target)
        if test1 is not None:
            target_precision = float(test1.group(2))
            target_element = test1.group(1)
            target_over_fe = False
        elif test2 is not None:
            target_precision = float(test2.group(2))
            target_element = test2.group(1)
            target_over_fe = True
        else:
            raise SyntaxError("Could not parse target {}".format(target))

        # Check that element is included in Cannon run
        label_name = "[{}/H]".format(target_element)
        assert label_name in cannon_output['labels']

        # Loop over all the reddening values we're considering
        for e_bv in ebv_values:
            cannon_data = data[star_name][e_bv]
            exposure_times = cannon_data.keys()
            exposure_times.sort()

            # Start making a list of the offsets of the Cannon's estimates as a function of exposure time
            offsets = []
            for exposure_time in exposure_times:
                x = cannon_data[exposure_time]
                target_key = "target_{}".format(label_name)
                # print x.keys()
                if target_key not in x:
                    x[target_key] = x["target_[Fe/H]"]  # If elemental abundance not in metadata, assume scaled solar
                offset = abs(x[label_name] - x[target_key])
                if target_over_fe:
                    offset -= abs(x["[Fe/H]"] - x["target_[Fe/H]"])
                offsets.append([x["SNR"], offset])

            # Interpolate exposure time needed to meet precision target
            exposure_time_needed = 1e6
            previous_offset = 1e6
            previous_exp_time = 0
            previous_snr = 0
            for i, exposure_time in enumerate(exposure_times):
                snr, new_offset = offsets[i]
                if new_offset > target_precision:
                    previous_offset = new_offset
                    previous_exp_time = exposure_time
                    previous_snr = snr
                    continue
                weight_a = abs(new_offset - target_precision)
                weight_b = abs(previous_offset - target_precision)
                exposure_time_needed = (previous_exp_time * weight_a + exposure_time * weight_b) / (weight_a + weight_b)
                snr_needed = (previous_snr * weight_a + snr * weight_b) / (weight_a + weight_b)
                break
            exposure[star_name][j][e_bv] = [exposure_time_needed, snr_needed]

# Write values to data files
for k, star_name in enumerate(star_names):
    filename = "{}_{:03d}.dat".format(args.output_stub, k)
    with open(filename, "w") as f:
        for j, target in enumerate(args.targets):
            for e_bv in ebv_values:
                exposure_time_needed, snr_needed = exposure[star_name][j][e_bv]
                f.write("%16s %16s %16s\n" % (e_bv, exposure_time_needed, snr_needed))
            f.write("\n\n")

    # Create pyxplot script to produce this plot
    width = float(args.width)
    aspect = 1 / 1.618034  # Golden ratio
    pyxplot_input = ""

    pyxplot_input += """
    
set nodisplay
set origin 0,0
set width {}
set size ratio {}
set fontsize 1.1
set nokey

set xlabel "$E(B-V)$"
set xrange [0.01:4]
set log x
set ylabel "Exposure time / min"
set yrange [1:1000]
set log y

set label 1 texify("{}") at page 0.5, page {}

""".format(width, aspect,
           star_name, width * aspect - 0.5)

    datasets = []
    for j, target in enumerate(args.targets):
        # Plot exposure times in minutes
        datasets.append(" \"{0}\" using $1:$2/60. index {1} title \"{2}\" with lines ".format(filename, j, target))


    pyxplot_input += """
    
set output "{0}.png"

plot {1}

""".format(filename, ",".join(datasets))

    pyxplot_input += """

set term eps ; set output '{0}.eps' ; set display ; refresh
set term png ; set output '{0}.png' ; set display ; refresh
set term pdf ; set output '{0}.pdf' ; set display ; refresh

""".format(filename)

    # Run pyxplot
    p = os.popen("pyxplot", "w")
    p.write(pyxplot_input)
    p.close()
