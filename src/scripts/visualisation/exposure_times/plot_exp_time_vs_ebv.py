#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python plot_exp_time_vs_ebv.py>, but <./plot_exp_time_vs_ebv.py> will not work.

"""
Take an output file from the Cannon, where stars have been run at a range of SNRs and E(B-V) values. Produce a plot
of the exposure time needed to yield various abundances to various precision targets.

python2.7 plot_exp_time_vs_ebv.py --abundance-target "[Fe/H]<0.1" --abundance-target "[Mg/Fe]<0.15" --abundance-target "["

"""

import os
from os import path as os_path
import sys
import argparse
import json
import re
import logging
import numpy as np
from operator import itemgetter

from fourgp_speclib import SpectrumLibrarySqlite
from lib.multiplotter import PyxplotDriver

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../..")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--abundance-target', action="append", dest='targets',
                    help="Abundances we're trying to recover with a given precision target.")
parser.add_argument('--cannon-output',
                    default="../../output_data/cannon/cannon_reddened_fourteam2_sample_hrs_10label.json",
                    dest='cannon',
                    help="Cannon output file we should analyse.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--output', default="/tmp/cannon_estimates_", dest='output_stub',
                    help="Data file to write output to.")
args = parser.parse_args()

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../../workspace")

# Read Cannon output
if not os.path.exists(args.cannon):
    print "scatter_plot_snr_required.py could not proceed: Cannon run <{}> not found".format(args.cannon)
    sys.exit()

cannon_output = json.loads(open(args.cannon).read())
print "Number of Cannon tests: {:d}".format(len(cannon_output['stars']))

# Create a sorted list of all the SNR values we've got
snr_values = [item['SNR'] for item in cannon_output['stars']]
snr_values = sorted(set(snr_values))
print "Number of SNR values: {:d}".format(len(snr_values))

# Create a sorted list of all the SNR definitions we've got
snr_definitions = [item['snr_definition'] for item in cannon_output['stars']]
snr_definitions = sorted(set(snr_definitions))
print "Number of SNR definitions: {:d}".format(len(snr_definitions))

# Create a sorted list of all the stars we've got
star_names = [item['Starname'] for item in cannon_output['stars']]
star_names = sorted(set(star_names))
print "Number of unique stars: {:d}".format(len(star_names))

# Create a sorted list of all the E(B-V) values we've got
ebv_values = [item['e_bv'] for item in cannon_output['stars']]
ebv_values = sorted(set(ebv_values))
print "Number of unique E(B-V) values: {:d}".format(len(ebv_values))

# Estimate number of observations in each configuration
print "Number of observations per configuration: {:.3f}".format(float(len(cannon_output['stars'])) / len(snr_values)
                                                                / len(snr_definitions) / len(star_names)
                                                                / len(ebv_values))

# If list of abundance constraints not specified, make some up
if args.targets is None:
    args.targets = ["[Fe/H]<0.1"]
    for label in cannon_output['labels']:
        test = re.match("\[(.*)/H\]", label)
        if test is not None:
            element = test.group(1)
            if element != "Fe":
                args.targets.append("[{}/Fe]<0.15".format(element))
logger.info("Targets are: {}".format(str(args.targets)))

# Work out multiplication factor to convert SNR/pixel to SNR/A
raster = np.array(cannon_output['wavelength_raster'])
raster_diff = np.diff(raster[raster > 6000])
pixels_per_angstrom = 1.0 / raster_diff[0]

# Open original spectrum library, so we can extract exposure time metadata
input_library_info = SpectrumLibrarySqlite.open_and_search(
    library_spec=cannon_output["test_library"],
    workspace=workspace,
    extra_constraints={"continuum_normalised": 1}
)

input_library, library_items = [input_library_info[i] for i in ("library", "items")]

# Loop over stars, reorganising data by star name and E(B-V)
data = {}
for star_index, star in enumerate(cannon_output['stars']):
    if (star_index % 1000) == 0:
        logger.info("Reading stellar parameters: {:7d}/{:7d}".format(star_index, len(cannon_output['stars'])))

    # Create data structure to receive metadata about this star
    object_name = star['Starname']
    if object_name not in data:
        data[object_name] = {}
    e_bv = star['e_bv']
    if e_bv not in data[object_name]:
        data[object_name][e_bv] = {}
    uid = star['uid']
    snr_value = float(star['SNR'])
    if snr_value not in data[object_name][e_bv]:
        data[object_name][e_bv][snr_value] = []

    # Fetch metadata about this star
    spectra_list = input_library.search(uid=uid, continuum_normalised=1)
    assert len(spectra_list) == 1, "Multiple spectra with the same UID"
    spectra_ids = [i["specId"] for i in spectra_list]
    metadata = input_library.get_metadata(ids=spectra_ids)[0]
    exposure_time = metadata['exposure']
    if not np.isfinite(exposure_time):
        exposure_time = 1e9
    data[object_name][e_bv][snr_value].append([float(exposure_time), star])

# Loop over stars, plotting each in turn
exposure = {}  # exposure[star_name][target][E_BV] = exposure time
for star_index, star_name in enumerate(star_names):
    logger.info("Calculating exposures: {:7d}/{:7d}".format(star_index, len(star_names)))

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

            # Start making a list of the offsets of the Cannon's estimates as a function of exposure time
            offset_vs_exposure = []

            # Loop over all SNR values (and definitions) we have
            for snr_value in data[star_name][e_bv]:
                observations = data[star_name][e_bv][snr_value]
                exposure_times = []
                offsets = []

                # Compile a list of exposure times and the Cannon's offsets
                for exposure_time, observation in observations:
                    target_key = "target_{}".format(label_name)
                    if target_key not in observation:
                        # If elemental abundance not in metadata, assume scaled solar
                        observation[target_key] = observation["target_[Fe/H]"]
                    offset = observation[label_name] - observation[target_key]
                    if target_over_fe:
                        offset = offset - (observation["[Fe/H]"] - observation["target_[Fe/H]"])
                    offsets.append(pow(offset, 2))
                    exposure_times.append(exposure_time)

                # Take average exposure time and abundance offsets
                exposure_time = np.mean(exposure_times)
                offset = np.sqrt(np.mean(offsets))

                offset_vs_exposure.append([exposure_time, snr_value, offset, len(exposure_times)])

            # Sort offset vs exposure time into order of descending exposure time
            offset_vs_exposure.sort(key=itemgetter(0))
            offset_vs_exposure.reverse()

            # Interpolate exposure time needed to meet precision target
            exposure_time_needed = 1e6
            previous_offset = 1e6
            previous_exp_time = 1e6
            previous_snr = 1e6
            # Cycle through SNRs from highest to lowest
            for configuration in offset_vs_exposure:
                exposure_time, snr, new_offset, n_points = configuration
                # If performance is satisfactory at this SNR, continue onto next one
                if new_offset < target_precision:
                    previous_offset = new_offset
                    previous_exp_time = exposure_time
                    previous_snr = snr
                    continue
                weight_a = abs(new_offset - target_precision)
                weight_b = abs(previous_offset - target_precision)
                exposure_time_needed = (previous_exp_time * weight_a + exposure_time * weight_b) / (weight_a + weight_b)
                snr_needed = (previous_snr * weight_a + snr * weight_b) / (weight_a + weight_b)
                break
            exposure[star_name][j][e_bv] = [exposure_time_needed, offset_vs_exposure, snr_needed]

# Instantiate pyxplot
plotter = PyxplotDriver()

# Write exposure time values to data files and plot them
for k, star_name in enumerate(star_names):
    # Write file listing E(B-V) and exposure time needed for each target
    filename = "{}_star{:03d}.dat".format(args.output_stub, k)
    with open(filename, "w") as f:
        f.write("# E(B-V)   Exposure time   # List of [exp_time, snr, offset, n_points]\n")
        for j, target in enumerate(args.targets):
            f.write("# Target: {}".format(target))
            for e_bv in ebv_values:
                exposure_time_needed, offsets, snr_needed = exposure[star_name][j][e_bv]
                f.write("{:16s} {:16s}   # {:s}\n".format(str(e_bv), str(exposure_time_needed), str(offsets)))
            f.write("\n\n")

    # Create pyxplot script to produce this plot
    # Plot exposure times in minutes
    plotter.make_plot(output_filename=filename, caption=star_name, pyxplot_script="""
    
set origin 0,0
set fontsize 1.1
set key below
set keycol 3

set xlabel "$E(B-V)$"
set xrange [0.03:3]
set log x
set ylabel "Exposure time / min"
set yrange [5:1200]
set log y

plot {plot_items}

""".format(plot_items=",".join(["""
"{filename}" using $1:$2 index {index} title "RMS error in {title}" with lines
    """.format(filename=filename,
               index=j,
               title=re.sub("<", " $<$ ", target)).strip()
                                for j, target in enumerate(args.targets)
                                ]))
                      )

# Write label-offset vs SNR values to data files and plot them for diagnostics
for k, star_name in enumerate(star_names):
    # Write files listing SNR and offset in each target
    for e_bv in ebv_values:
        filename2 = "{}_star{:03d}_ebv_{:05.2f}.dat".format(args.output_stub, k, e_bv)
        with open(filename2, "w") as f:
            f.write("# SNR")
            for j, target in enumerate(args.targets):
                f.write("   Offset_{}".format(target))
            f.write("\n")
            for i in range(len(exposure[star_name][0][e_bv][1])):
                snr_value = exposure[star_name][0][e_bv][1][i][1]
                f.write("{:16s} ".format(str(snr_value)))
                for j, target in enumerate(args.targets):
                    offset = exposure[star_name][j][e_bv][1][i][2]
                    f.write("{:16s} ".format(str(offset)))
                f.write("  # Average of {:d} points; exposure time {:6.1f} min\n".
                        format(exposure[star_name][0][e_bv][1][i][3], exposure[star_name][0][e_bv][1][i][0]))

        # Create pyxplot script to produce this plot
        # Plot exposure times in minutes
        plotter.make_plot(output_filename=filename2, caption=star_name, pyxplot_script="""
    
set origin 0,0
set fontsize 1.1
set key below
set keycol 3

set xlabel "SNR/pixel"
set xrange [10:250]
set log x
set ylabel "RMS offset in abundance"
set yrange [0:0.5]

plot {plot_items}

""".format(plot_items=",".join(["""
"{filename}" using 1:{column:d} title "{title}" with lines
    """.format(filename=filename2,
               column=2 + j,
               title=re.sub("<", " $<$ ", target)
               ).strip()
                                for j, target in enumerate(args.targets)
                                ]))
                          )

# Clean up plotter
del plotter
