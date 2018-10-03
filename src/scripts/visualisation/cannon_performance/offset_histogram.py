#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python mean_performance_vs_label.py>, but <./mean_performance_vs_label.py> will not work.

"""
Plot results of testing the Cannon against noisy test spectra, to see how well it reproduces stellar labels.
"""

import gzip
import json
import os
import re
from os import path as os_path

import numpy as np
from fourgp_degrade import SNRConverter
from lib.abscissa_information import AbscissaInformation
from lib.compute_cannon_offsets import CannonAccuracyCalculator
from lib.label_information import LabelInformation
from lib.plot_settings import snr_defined_at_wavelength, plot_width
from lib.pyxplot_driver import PyxplotDriver
from offset_cmd_line_interface import fetch_command_line_arguments


def generate_histograms(data_sets, abscissa_label, assume_scaled_solar,
                        compare_against_reference_labels, output_figure_stem, run_title,
                        abundances_over_h=True):
    """
    Create a set of plots of a number of Cannon runs.

    :param data_sets:
        A list of runs of the Cannon which are to be plotted. This should be a list of dictionaries. Each dictionary
        should have the entries:

        cannon_output: The filename of the JSON output file from the Cannon, without the ".summary.json.gz" suffix.
        title: Legend caption to use for each Cannon run.
        filters: A string containing semicolon-separated set of constraints on stars we are to include.
        colour: The colour to plot the dataset in.
        line_type: The Pyxplot line type to use for this Cannon run.


    :param abscissa_label:
        The name of the label we are to plot on the horizontal axis. This should be 'SNR/A', 'SNR/pixel', 'ebv'. See
        <lib/abscissa_information.py>, where these are defined.

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
    label_metadata = LabelInformation().label_metadata

    # Metadata data about all of the horizontal axes that we can plot precision against
    abscissa_info = AbscissaInformation().abscissa_labels[abscissa_label]

    # Look up a list of all the (unique) labels the Cannon tried to fit in all the data sets we're plotting
    unique_json_files = set([item['cannon_output'] for item in data_sets])
    labels_in_each_data_set = [json.loads(gzip.open(json_file + ".summary.json.gz", "rt").read())['labels']
                               for json_file in unique_json_files]
    unique_labels = set([label for label_list in labels_in_each_data_set for label in label_list])

    # Filter out any labels where we don't have metadata about how to plot them
    label_names = [item for item in unique_labels if item in label_metadata]

    # LaTeX strings to use to label each stellar label on graph axes
    labels_info = [label_metadata[ln] for ln in label_names]

    # Create directory to store output files in
    os.system("mkdir -p {}".format(output_figure_stem))

    data_set_titles = []
    output_figure_stem = os_path.abspath(output_figure_stem) + "/"
    data_set_counter = -1
    plot_histograms = [[{} for j in data_sets] for i in label_names]

    # If requested, plot all abundances (apart from Fe) over Fe
    if not abundances_over_h:
        for j, label_name in enumerate(label_names):
            test = re.match("\[(.*)/H\]", label_name)
            if test is not None:
                if test.group(1) != "Fe":
                    label_names[j] = "[{}/Fe]".format(test.group(1))

    # Loop over the various Cannon runs we have, e.g. LRS and HRS
    data_file_names = []
    for counter, data_set in enumerate(data_sets):

        cannon_output = json.loads(gzip.open(data_set['cannon_output'] + ".full.json.gz", "rt").read())

        # If no label has been specified for this Cannon run, use the description field from the JSON output
        if data_set['title'] is None:
            data_set['title'] = re.sub("_", r"\_", cannon_output['description'])

        # Calculate the accuracy of the Cannon's abundance determinations
        accuracy_calculator = CannonAccuracyCalculator(
            cannon_json_output=cannon_output,
            label_names=label_names,
            compare_against_reference_labels=compare_against_reference_labels,
            assume_scaled_solar=assume_scaled_solar,
            abscissa_field=abscissa_info['field']
        )

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

        # Create a sorted list of all the abscissa values we've got
        abscissa_values = list(accuracy_calculator.label_offsets.keys())
        abscissa_values = sorted(set(abscissa_values))

        data_set_counter += 1

        # Construct a datafile listing all the offsets for each label, for each abscissa value
        # This full list of data points is used to make histograms
        for abscissa_index, abscissa_value in enumerate(abscissa_values):
            displayed_abscissa_value = abscissa_value
            if abscissa_label == "SNR/A":
                displayed_abscissa_value = snr_converter.per_pixel(abscissa_value).per_a()

            # Filename for data file containing all offsets
            data_file = "{}/data_offsets_all_{:d}_{:06.1f}.dat".format(output_figure_stem,
                                                                       data_set_counter,
                                                                       displayed_abscissa_value)

            y = []
            for i, (label_name, label_info) in enumerate(zip(label_names, labels_info)):
                # List of offsets
                diffs = accuracy_calculator.label_offsets[abscissa_value][label_name]
                y.append(diffs)

                # Output histogram of label mismatches at this abscissa value
                # i+1 is because Pyxplot counts columns starting from 1, not 0
                plot_histograms[i][data_set_counter][displayed_abscissa_value] = [(data_file, snr_converter, i + 1)]

            # Output data file of label mismatches at this abscissa value
            np.savetxt(fname=data_file,
                       X=np.transpose(y),
                       header="""
# Each row represents a star
# {column_headings}

""".format(column_headings="     ".join(["offset_{}".format(x) for x in label_names]))
                       )

            data_file_names.append(data_file)

        del cannon_output

    # Now plot the data

    # Create pyxplot script to produce this plot
    plotter = PyxplotDriver(multiplot_filename="{}/histogram_multiplot".format(output_figure_stem),
                            width=plot_width * 1.5,  # Plot histograms larger than other plots, because so many lines
                            multiplot_aspect=6. / 8)

    # Create a new pyxplot script for precision plots
    for i, (label_name, label_info) in enumerate(zip(label_names, labels_info)):

        # Create a new pyxplot script for histogram plots
        for data_set_counter, data_set_items in enumerate(plot_histograms[i]):

            plot_items = []
            k_max = float(len(data_set_items) - 1)
            if k_max < 1:
                k_max = 1.

            for abscissa_index, (displayed_abscissa_value, items) in enumerate(sorted(data_set_items.items())):
                for j, (plot_item, snr_converter, column) in enumerate(items):

                    if abscissa_label == "SNR/A":
                        snr = snr_converter.per_a(displayed_abscissa_value)
                        caption = "SNR/A {0:.1f}; SNR/pixel {1:.1f}". \
                            format(snr.per_a(), snr.per_pixel())
                    elif abscissa_label == "SNR/pixel":
                        snr = snr_converter.per_pixel(displayed_abscissa_value)
                        caption = "SNR/A {0:.1f}; SNR/pixel {1:.1f}". \
                            format(snr.per_a(), snr.per_pixel())
                    else:
                        caption = "{0} {1}".format(abscissa_info["latex"], displayed_abscissa_value)

                    plot_items.append("f_{0:d}_{1:.0f}(x) with lines colour col_scale({3}) title '{2:s}'".
                                      format(j, displayed_abscissa_value, caption, abscissa_index / k_max))

            plotter.make_plot(output_filename="{}/histogram_{:d}_{:d}".format(output_figure_stem, i, data_set_counter),
                              data_files=data_file_names,
                              caption="""
                              
{label_name}; {data_set_title}
                              """.format(
                                  label_name=label_info["latex"],
                                  data_set_title=data_set_titles[data_set_counter]
                              ).strip(),
                              pyxplot_script="""

set numerics errors quiet
set key ycentre right
set binwidth {bin_width}
col_scale(z) = hsb(0.75 * z, 1, 1)

set fontsize 1.3
set xlabel "$\Delta$ {label_name}"
set ylabel "Number of stars per unit {label_name}"
set xrange [{x_min}:{x_max}]

{make_histograms}

plot {plot_items}

                              """.format(
                                  bin_width=label_info["offset_max"] / 60.,
                                  label_name=label_info["latex"],
                                  x_min=-label_info["offset_max"] * 1.2,
                                  x_max=label_info["offset_max"] * 1.2,
                                  make_histograms="".join(["""
histogram f_{0:d}_{1:.0f}() \"{2}\" using {3}
                                  """.format(j, displayed_abscissa_value, data_item, column)
                                                           for abscissa_index, (displayed_abscissa_value, data_items) in
                                                           enumerate(sorted(data_set_items.items()))
                                                           for j, (data_item, snr_converter, column) in
                                                           enumerate(data_items)
                                                           ]),
                                  plot_items=",".join(plot_items)
                              )
                              )


if __name__ == "__main__":
    # Read input parameters
    command_line_arguments = fetch_command_line_arguments()
    generate_histograms(**command_line_arguments)
