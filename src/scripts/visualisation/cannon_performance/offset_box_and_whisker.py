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
from lib.plot_settings import snr_defined_at_wavelength
from lib.snr_conversion import SNRConverter

from offset_cmd_line_interface import fetch_command_line_arguments


def generate_box_and_whisker_plots(data_sets, abscissa_label, assume_scaled_solar,
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

    # Metadata about all the labels which we can plot the Cannon's precision in estimating
    label_info = LabelInformation().label_info

    # Metadata data about all of the horizontal axes that we can plot precision against
    abscissa_info = AbcissaInformation().abscissa_labels[abscissa_label]

    # Look up a list of all the (unique) labels the Cannon tried to fit in all the data sets we're plotting
    unique_json_files = set([item['cannon_output'] for item in data_sets])
    labels_in_each_data_set = [json.loads(open(json_file).read())['labels'] for json_file in unique_json_files]
    unique_labels = set([label for label_list in labels_in_each_data_set for label in label_list])

    # Filter out any labels where we don't have metadata about how to plot them
    label_names = [item for item in unique_labels if item in label_info]

    # Create directory to store output files in
    os.system("mkdir -p {}".format(output_figure_stem))

    data_set_titles = []
    output_figure_stem = os_path.abspath(output_figure_stem) + "/"
    data_set_counter = -1
    plot_box_whiskers = [[[] for j in data_sets] for i in label_names]

    # If requested, plot all abundances (apart from Fe) over Fe
    if not abundances_over_h:
        for j, label_name in enumerate(label_names):
            test = re.match("\[(.*)/H\]", label_name)
            if test is not None:
                if test.group(1) != "Fe":
                    label_names[j] = "[{}/Fe]".format(test.group(1))

    common_x_limits = abscissa_info["axis_range"]

    # Loop over the various Cannon runs we have, e.g. LRS and HRS
    for counter, data_set in enumerate(data_sets):

        cannon_output = json.loads(open(data_set['cannon_output']).read())

        # If no label has been specified for this Cannon run, use the description field from the JSON output
        if data_set['title'] is None:
            data_set['title'] = cannon_output['description']

        # Calculate the accuracy of the Cannon's abundance determinations
        accuracy_calculator = CannonAccuracyCalculator(
            cannon_json_output=cannon_output,
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

        # Work out multiplication factor to convert SNR/pixel to SNR/A
        snr_converter = SNRConverter(raster=np.array(cannon_output['wavelength_raster']),
                                     snr_at_wavelength=snr_defined_at_wavelength)

        data_set_titles.append(legend_label)

        # LaTeX strings to use to label each stellar label on graph axes
        labels_info = [label_info[ln] for ln in label_names]

        # Create a sorted list of all the abscissa values we've got
        abscissa_values = [item[abscissa_info["field"]] for item in cannon_stars]
        abscissa_values = sorted(set(abscissa_values))

        # If all abscissa values are off the range of the x axis, rescale axis
        if common_x_limits is not None:
            if abscissa_values[0] > common_x_limits[1]:
                common_x_limits[1] = abscissa_values[0]
                print "Rescaling x-axis to include {:.1f}".format(abscissa_values[0])
            if abscissa_values[-1] < common_x_limits[0]:
                common_x_limits[0] = abscissa_values[-1]
                print "Rescaling x-axis to include {:.1f}".format(abscissa_values[-1])

        data_set_counter += 1

        # Construct a data file listing the RMS and percentiles of the offset distribution for each label
        for i, (label_name, label_info) in enumerate(zip(label_names, labels_info)):
            y = []
            for abscissa_index, abscissa_value in enumerate(abscissa_values):
                displayed_abscissa_value = abscissa_value
                if abscissa_label == "SNR/A":
                    displayed_abscissa_value = snr_converter.per_pixel(abscissa_value).per_a()

                # List of offsets
                diffs = label_offset[abscissa_value][label_name]

                # Sort list
                diffs.sort()

                def percentile(fraction):
                    return diffs[int(fraction / 100. * len(diffs))]

                y.append([])
                y[-1].extend([displayed_abscissa_value])
                y[-1].extend([percentile(5), percentile(25), percentile(50), percentile(75), percentile(95)])

            # Filename for data containing statistics on percentiles of the offset distributions
            file_name = "{}data_offsets_dist_{:d}_{:d}.dat".format(output_figure_stem, i, data_set_counter)

            # Output table of statistical measures of label-mismatch-distribution as a function of abscissa
            # Subsequent columns are various percentiles (see above)
            np.savetxt(fname=file_name,
                       X=y,
                       header="""
# Abscissa_(probably_SNR)     5th_percentile     25th_percentile    Median    75th_percentile     95th_percentile

""")

            plot_box_whiskers[i][data_set_counter] = [
                "\"{}\" using 1:5:3:7 with yerrorrange col black".format(file_name)
            ]

            # Filename for data used to make box-and-whisker diagrams, with boxes explicitly defined
            file_name = "{}data_whiskers_{:d}_{:d}.dat".format(output_figure_stem, i, data_set_counter)

            with open(file_name, "w") as f:
                f.write("""
# Each block within this file represents a rectangular region to shade on a box-and-whisker plot
# x y

""")
                for j, datum in enumerate(y):
                    if abscissa_label.startswith("SNR"):
                        w1 = 1.2
                        w2 = 1
                    else:
                        w1 = 0
                        w2 = 1.024
                    f.write("{} {}\n".format((datum[0] - w1) / w2, datum[3]))
                    f.write("{} {}\n".format((datum[0] - w1) / w2, datum[5]))
                    f.write("{} {}\n".format((datum[0] + w1) * w2, datum[5]))
                    f.write("{} {}\n\n\n".format((datum[0] + w1) * w2, datum[3]))

                    plot_box_whiskers[i][data_set_counter]. \
                        insert(0, "\"{0}\" using 1:2 with filledregion fc red col black lw 0.5 index {1}".
                               format(file_name, j))

        del cannon_output

    # Now plot the data

    # LaTeX strings to use to label each stellar label on graph axes
    labels_info = [label_info[ln] for ln in label_names]

    # Create pyxplot script to produce this plot
    plotter = PyxplotDriver(multiplot_filename="whiskers_multiplot".format(output_figure_stem),
                            multiplot_aspect=6. / 8)

    # Create a new pyxplot script for precision plots
    for i, (label_name, label_info) in enumerate(zip(label_names, labels_info)):

        # Create a new pyxplot script for box and whisker plots
        for data_set_counter, plot_items in enumerate(plot_box_whiskers[i]):
            plotter.make_plot(output_filename="{}whiskers_{:d}_{:d}".format(output_figure_stem, i, data_set_counter),
                              caption="""
{label_name}; {data_set_title}
                              """.format(
                                  label_name=label_info["latex"],
                                  data_set_title=data_set_titles[data_set_counter]
                              ).strip(),
                              pyxplot_script="""
set nokey
set fontsize 1.3
set ylabel "$\Delta$ {label_name}"
set xlabel "{x_label}"
set yrange [{y_min}:{y_max}]
{set_log}
{set_x_range}

plot {plot_items}
      
                              """.format(
                                  label_name=label_info["latex"],
                                  x_label=abscissa_info["latex"],
                                  y_min=-2 * label_info["offset_max"],
                                  y_max=2 * label_info["offset_max"],
                                  set_log=("set log x" if abscissa_info["log_axis"] else ""),
                                  set_x_range=("set xrange [{}:{}]".format(common_x_limits[0], common_x_limits[1])
                                               if common_x_limits is not None else ""),
                                  plot_items=",".join(plot_items)
                              )
                              )


if __name__ == "__main__":
    # Read input parameters
    command_line_arguments = fetch_command_line_arguments()
    generate_box_and_whisker_plots(**command_line_arguments)
