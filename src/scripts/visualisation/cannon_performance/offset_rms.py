#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python mean_performance_vs_label.py>, but <./mean_performance_vs_label.py> will not work.

"""
Plot results of testing the Cannon against noisy test spectra, to see how well it reproduces stellar labels.
"""

import os
from os import path as os_path
import re
import numpy as np
import json

from lib.pyxplot_driver import PyxplotDriver
from lib.label_information import LabelInformation
from lib.abscissa_information import AbcissaInformation
from lib.compute_cannon_offsets import CannonAccuracyCalculator

from offset_cmd_line_interface import fetch_command_line_arguments


def generate_rms_precision_plots(data_sets, abscissa_label, assume_scaled_solar,
                                 compare_against_reference_labels, output_figure_stem, run_title,
                                 abundances_over_h=True):
    """
    Create a set of plots of a number of Cannon runs.

    :param data_sets:
        A list of runs of the Cannon which are to be plotted. This should be a list of dictionaries. Each dictionary
        should have the entries:

        cannon_output: The filename of the JSON output file from the Cannon.
        title: Legend caption to use for each Cannon run.
        filters: A string containing semicolon-separated set of constraints on stars we are to include.
        colour: The colour to plot the dataset in.
        line_type: The Pyxplot line type to use for this Cannon run.


    :param abscissa_label:
        The name of the label we are to plot on the horizontal axis. This should be 'SNR/A', 'SNR/pixel', 'ebv'. See
        <lib/abcissa_information.py>, where these are defined.

    :param compare_against_reference_labels:
        If true, we measure the difference between each label value estimated by the Cannon and the target value taken
        from that star's metadata in the original spectrum library. I.e. the value used to synthesise the spectrum.

        If false, we measure the deviation from the value for each label estimated at the highest abscissa value -- e.g.
        highest SNR.

    :param output_figure_stem:
        Directory to save plots in

    :param run_title:
        A suffix to put at the end of the label in the top-left corner of each plot

    :param abundances_over_h:
        Boolean flag to select whether we plot abundances over H or Fe.

    :return:
        None
    """

    label_info = LabelInformation().label_info

    abscissa_info = AbcissaInformation().abscissa_labels

    # Create directory to store output files in
    os.system("mkdir -p {}".format(output_figure_stem))

    output_figure_stem = os_path.abspath(output_figure_stem) + "/"
    data_set_counter = -1
    plot_precision = [[] for i in label_names]

    # Work out list of labels to plot, based on first data set we're provided with
    data_set_0 = json.loads(open(data_sets[0]['cannon_output']).read())
    label_names = [item for item in data_set_0['labels'] if item in label_info]
    del data_set_0

    # If requested, plot all abundances (apart from Fe) over Fe
    if not abundances_over_h:
        for j, label_name in enumerate(label_names):
            test = re.match("\[(.*)/H\]", label_name)
            if test is not None:
                if test.group(1) != "Fe":
                    label_names[j] = "[{}/Fe]".format(test.group(1))

    common_x_limits = abscissa_info[3]

    # Loop over the various Cannon runs we have, e.g. LRS and HRS
    for counter, data_set in enumerate(data_sets):

        data = json.loads(open(data_set['cannon_output']).read())

        # If no label has been specified for this Cannon run, use the description field from the JSON output
        if data_set['title'] is None:
            data_set['title'] = data['description']

        # Calculate the accuracy of the Cannon's abundance determinations
        accuracy_calculator = CannonAccuracyCalculator(
            cannon_json_output=data,
            label_names=label_names,
            compare_against_reference_labels=compare_against_reference_labels,
            assume_scaled_solar=assume_scaled_solar)

        stars_which_meet_filter = accuracy_calculator.filter_test_stars(constraints=data_set['filters'].split(";"))

        accuracy_calculator.calculate_cannon_offsets(filter_on_indices=stars_which_meet_filter)

        # Add data set to plot
        legend_label = data_set['title']  # Read the title which was supplied on the command line for this dataset
        if run_title:
            legend_label += " ({})".format(run_title)  # Possibly append a run title to the end, if supplied

        # add data set

        # Convert SNR/pixel to SNR/A at 6000A
        raster = np.array(cannon_json['wavelength_raster'])
        raster_diff = np.diff(raster[raster > 6000])
        pixels_per_angstrom = 1.0 / raster_diff[0]

        datasets.append(legend_label)

        # LaTeX strings to use to label each stellar label on graph axes
        labels_info = [label_info[ln] for ln in label_names]

        # Create a sorted list of all the abscissa values we've got
        abscissa_info = abscissa_labels[abscissa_label]
        abscissa_values = [item[abscissa_info[0]] for item in cannon_stars]
        abscissa_values = sorted(set(abscissa_values))

        # If all abscissa values are off the range of the x axis, rescale axis
        if common_x_limits is not None:
            if abscissa_values[0] > common_x_limits[1]:
                common_x_limits[1] = abscissa_values[0]
                print "Rescaling x-axis to include {.1f}".format(abscissa_values[0])
            if abscissa_values[-1] < common_x_limits[0]:
                common_x_limits[0] = abscissa_values[-1]
                print "Rescaling x-axis to include {.1f}".format(abscissa_values[-1])

        data_set_counter += 1

        # Construct a data file listing the RMS and percentiles of the offset distribution for each label
        for i, (label_name, label_info) in enumerate(zip(label_names, labels_info)):
            scale = np.sqrt(pixels_per_angstrom)

            y = []
            for k, xk in enumerate(abscissa_values):
                snr_per_a = None
                if abscissa_label.startswith("SNR"):
                    snr_per_a = xk * scale

                keyword = snr_per_a if abscissa_label == "SNR/A" else xk

                # List of offsets
                diffs = label_offset[xk][label_name]

                # Sort list
                diffs.sort()

                y.append([])
                y[-1].extend([keyword])
                y[-1].extend([metric(diffs)])

            # Filename for data containing statistics on the RMS, and percentiles of the offset distributions
            file_name = "{}data_offsets_rms_{:d}_{:d}.dat".format(output_figure_stem, i, data_set_counter)

            # Output table of statistical measures of label-mismatch-distribution as a function of abscissa
            # 1st column is RMS.
            np.savetxt(fname=file_name, X=y, header=
            "# Abscissa_(probably_SNR)     RMS_offset\n\n"
                       )

            plot_precision[i].append([
                "\"{}\" using 1:2".format(file_name),
                legend_label,
                "with lp pt 17 col {} lt {:d}".format(colour, int(line_type)),
                len(star_names),
            ])

        del data

    # make plots

    # LaTeX strings to use to label each stellar label on graph axes
    labels_info = [label_info[ln] for ln in label_names]

    abscissa_info = abscissa_labels[abscissa_label]

    # Create pyxplot script to produce this plot
    plotter_all = PyxplotDriver(multiplot_filename="precision_all_multiplot".format(output_figure_stem),
                                multiplot_aspect=6. / 8)

    plotter = PyxplotDriver(multiplot_filename="precision_multiplot".format(output_figure_stem),
                            multiplot_aspect=6. / 8)

    # Create a new pyxplot script for precision in all elements in one plot
    for j in range(len(plot_precision[0])):
        plotter_all.make_plot(output_filename="{}precisionall_{:d}".format(output_figure_stem, j),
                              caption=r"""
{title} ({star_count} stars)
                              """.format(
                                  title=plot_precision[2][j][1],
                                  star_count=plot_precision[2][j][3]
                              ).strip(),
                              pyxplot_script="""

set fontsize 1.3
set key top {keypos}
set keycols 2
set ylabel "RMS offset in abundance [dex]"
set xlabel "{x_label}"
set yrange [0:0.5]
{set_log}
{set_x_range}

plot {plot_items}
                              """.format(
                                  keypos="right" if abscissa_info[0] == "SNR" else "left",
                                  x_label=abscissa_info["latex"],
                                  set_log=("set log x" if abscissa_info[2] else ""),
                                  set_x_range=("set xrange [{}:{}]".format(common_x_limits[0], common_x_limits[1])
                                               if common_x_limits is not None else ""),
                                  plot_items=", ".join(["""
{filename} title "{title}" w lp pt {point_type}
                                      """.format(
                                      filename=plot_precision[i][j],
                                      title=label_info["latex"][:-13],  # Remove string "[dex]" from end of label
                                      point_type=16 + (i - 2)
                                  ).strip()
                                                        for i, (label_name, label_info) in
                                                        enumerate(zip(label_names, labels_info))
                                                        if label_name.startswith("[")
                                                        ] + ["""
{target} with lines col grey(0.75) notitle
                                      """.format(
                                      target=target_value
                                  ).strip()
                                                             for target_value in (0.1, 0.2)
                                                             ])
                              )
                              )

    # Create a new pyxplot script for precision plots
    for i, (label_name, label_info) in enumerate(zip(label_names, labels_info)):
        plotter_all.make_plot(output_filename="{}precision_{:d}".format(output_figure_stem, i),
                              caption=label_info["latex"],
                              pyxplot_script="""
                                  
{set_key}
set fontsize 1.3
set ylabel "RMS offset in {y_label}"
set xlabel "{x_label}"
set yrange [{y_min}:{y_max}]
{set_log}
{set_x_range}

plot {plot_items}

                                  """.format(
                                  set_key=("set key top {}".format("right"
                                                                   if abscissa_info[0] == "SNR"
                                                                   else "left")
                                           if (len(plot_precision[i]) > 1)
                                           else "set nokey"),
                                  x_label=abscissa_info["latex"],
                                  y_label=label_info["latex"],
                                  y_min=label_info["offset_min"],
                                  y_max=label_info["offset_max"],
                                  set_log=("set log x" if abscissa_info[2] else ""),
                                  set_x_range=("set xrange [{}:{}]".format(common_x_limits[0], common_x_limits[1])
                                               if common_x_limits is not None else ""),
                                  plot_items=", ".join(["""
{filename} title "{title} ({star_count} stars)" {style}
                                      """.format(
                                      **item
                                  ).strip()
                                                        for item in plot_precision[i]
                                                        ] + ["""
{target} with lines col grey(0.75) notitle
                                      """.format(
                                      target=target_value
                                  ).strip()
                                                             for target_value in label_info["targets"]
                                                             ])

                              )
                              )


if __name__ == "__main__":
    # Read input parameters
    command_line_arguments = fetch_command_line_arguments()
    generate_rms_precision_plots(**command_line_arguments)
