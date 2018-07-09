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
import time
import pwd
import sys
import re
import argparse
import numpy as np
import json

from lib.multiplotter import PyxplotDriver
from lib.label_information import LabelInformation
from lib.abscissa_information import AbcissaInformation
from lib.compute_cannon_offsets import CannonAccuracyCalculator


class PlotLabelPrecision:
    """
    Class for making a plot of the Cannon's performance.

    :ivar label_info:
        A tuple containing LaTeX labels to use on the figure axes.

    :ivar plot_counter:
        An integer counter used to give plots for each stellar label a unique filename.
    """

    def __init__(self,
                 label_names,
                 number_data_sets,
                 abscissa_label="SNR/A",
                 common_x_limits=None,
                 output_figure_stem="/tmp/cannon_performance/",
                 ):
        """

        :param label_names:
            A tuple containing the names of the labels we are to plot the precision for.

        :param number_data_sets:
            The number of Cannon runs we're going to plot.

        :param abscissa_label:
            The name of the label to be plotted along the horizontal axis of the performance plots.

        :param common_x_limits:
            A two-length tuple containing the lower and upper limits to set on all
            x axes.

        :param output_figure_stem:
            The file path where we are to save plots, pyxplot scripts and data files.
        """

        # Create directory to store output files in
        os.system("mkdir -p {}".format(output_figure_stem))

        # Fetch a list of the labels we produce performance plots for
        self.label_info = LabelInformation().label_info

        # All of the horizontal axes we can plot precision against. The parameter "abscissa_label" should be one of the
        # keys to this dictionary.
        self.abscissa_labels = AbcissaInformation().abscissa_labels

        self.datasets = []
        self.label_names = label_names
        self.abscissa_label = abscissa_label
        self.number_data_sets = number_data_sets
        self.common_x_limits = common_x_limits
        self.output_figure_stem = os_path.abspath(output_figure_stem) + "/"
        self.data_set_counter = -1
        self.plot_box_whiskers = [[[] for j in range(number_data_sets)] for i in label_names]

    def add_data_set(self, cannon_stars, cannon_json, label_reference_values,
                     legend_label=None,
                     colour="red", line_type=1,
                     metric=lambda x: np.sqrt(np.mean(np.square(x)))
                     ):
        """
        Add a data set to a set of precision plots.

        :param cannon_stars:
            The 'stars' structure from the JSON output from this run on the Cannon. Takes the form of a list of
            dictionaries containing the label values output by the Cannon in each test.

        :param label_reference_values:
            A dictionary of dictionaries containing reference values for the labels for each star.
            label_reference_values[star_name][label_name] = target_value

        :param legend_label:
            The label which should appear in the figure legend for this data set. This is typically the title
            supplied on the command line with the link to this Cannon run.

        :param colour:
            The colour of this data set. Should be specified as a valid Pyxplot string describing a colour.

        :param line_type:
            The Pyxplot line type to use for this data set. Should be specified as an integer.

        :param metric:
            A function used as a metric to convert a numpy array of absolute offsets into an average offset.

        :return:
            None
        """

        # Convert SNR/pixel to SNR/A at 6000A
        raster = np.array(cannon_json['wavelength_raster'])
        raster_diff = np.diff(raster[raster > 6000])
        pixels_per_angstrom = 1.0 / raster_diff[0]

        self.datasets.append(legend_label)

        # LaTeX strings to use to label each stellar label on graph axes
        labels_info = [self.label_info[ln] for ln in self.label_names]

        # Create a sorted list of all the abscissa values we've got
        abscissa_info = self.abscissa_labels[self.abscissa_label]
        abscissa_values = [item[abscissa_info[0]] for item in cannon_stars]
        abscissa_values = sorted(set(abscissa_values))

        # If all abscissa values are off the range of the x axis, rescale axis
        if self.common_x_limits is not None:
            if abscissa_values[0] > self.common_x_limits[1]:
                self.common_x_limits[1] = abscissa_values[0]
                print "Rescaling x-axis to include {.1f}".format(abscissa_values[0])
            if abscissa_values[-1] < self.common_x_limits[0]:
                self.common_x_limits[0] = abscissa_values[-1]
                print "Rescaling x-axis to include {.1f}".format(abscissa_values[-1])

        self.data_set_counter += 1

        # Construct a data file listing the RMS and percentiles of the offset distribution for each label
        for i, (label_name, label_info) in enumerate(zip(self.label_names, labels_info)):
            scale = np.sqrt(pixels_per_angstrom)

            y = []
            for k, xk in enumerate(abscissa_values):
                snr_per_a = None
                if self.abscissa_label.startswith("SNR"):
                    snr_per_a = xk * scale

                keyword = snr_per_a if self.abscissa_label == "SNR/A" else xk

                # List of offsets
                diffs = label_offset[xk][label_name]

                # Sort list
                diffs.sort()

                def percentile(fraction):
                    return diffs[int(fraction / 100. * len(diffs))]

                y.append([])
                y[-1].extend([keyword])
                y[-1].extend(
                    [metric(diffs), percentile(5), percentile(25), percentile(50), percentile(75), percentile(95)])

            # Filename for data containing statistics on the RMS, and percentiles of the offset distributions
            file_name = "{}data_offsets_rms_{:d}_{:d}.dat".format(self.output_figure_stem, i, self.data_set_counter)

            # Output table of statistical measures of label-mismatch-distribution as a function of abscissa
            # 1st column is RMS. Subsequent columns are various percentiles (see above)
            np.savetxt(fname=file_name, X=y, header=
            "# Abscissa_(probably_SNR)     RMS_offset     5th_percentile     25th_percentile    Median    75th_percentile     95th_percentile\n\n"
                       )

            self.plot_precision[i].append([
                "\"{}\" using 1:2".format(file_name),
                legend_label,
                "with lp pt 17 col {} lt {:d}".format(colour, int(line_type)),
                len(star_names),
            ])

            self.plot_box_whiskers[i][self.data_set_counter] = [
                "\"{}\" using 1:5:3:7 with yerrorrange col black".format(file_name)
            ]

            # Filename for data used to make box-and-whisker diagrams, with boxes explicitly defined
            file_name = "{}data_whiskers_{:d}_{:d}.dat".format(self.output_figure_stem, i, self.data_set_counter)

            with open(file_name, "w") as f:
                f.write(
                    "# Each block within this file represents a rectangular region to shade on a box-and-whisker plot\n"
                    "# x y\n\n"
                )
                for j, datum in enumerate(y):
                    if self.abscissa_label.startswith("SNR"):
                        w1 = 1.2
                        w2 = 1
                    else:
                        w1 = 0
                        w2 = 1.024
                    f.write("{} {}\n".format((datum[0] - w1) / w2, datum[3]))
                    f.write("{} {}\n".format((datum[0] - w1) / w2, datum[5]))
                    f.write("{} {}\n".format((datum[0] + w1) * w2, datum[5]))
                    f.write("{} {}\n\n\n".format((datum[0] + w1) * w2, datum[3]))

                    self.plot_box_whiskers[i][self.data_set_counter]. \
                        insert(0, "\"{0}\" using 1:2 with filledregion fc red col black lw 0.5 index {1}".
                               format(file_name, j))

    def make_plots(self):
        user_name = pwd.getpwuid(os.getuid()).pw_gecos.split(",")[0]
        plot_creator = "{}, {}".format(user_name, time.strftime("%d %b %Y"))

        aspect = 1 / 1.618034  # Golden ratio

        # LaTeX strings to use to label each stellar label on graph axes
        labels_info = [self.label_info[ln] for ln in self.label_names]

        abscissa_info = self.abscissa_labels[self.abscissa_label]

        # Create a new pyxplot script for precision plots
        for i, (label_name, label_info) in enumerate(zip(self.label_names, labels_info)):


            # Create a new pyxplot script for box and whisker plots
            for data_set_counter, plot_items in enumerate(self.plot_box_whiskers[i]):
                stem = "{}whiskers_{:d}_{:d}".format(self.output_figure_stem, i, data_set_counter)
                with open("{}.ppl".format(stem), "w") as ppl:
                    ppl.write("""
                
                    set width {0}
                    set size ratio {1}
                    set term dpi 400
                    set nokey
                    set nodisplay ; set multiplot
                    set label 1 "\\parbox{{{5}cm}}{{ {2}; {3} }}" page 0.2, page {4}
                    
                    """.format(self.plot_width, aspect, label_info["latex"], self.datasets[data_set_counter],
                               self.plot_width * aspect + 0.2, self.plot_width * 0.5))

                    if self.date_stamp:
                        ppl.write("""
                        set fontsize 0.8
                        text "{}" at 0, {}
                        """.format(plot_creator, self.plot_width * aspect + 0.4))

                    ppl.write("set fontsize 1.3\n")  # 1.6
                    ppl.write("set ylabel \"$\Delta$ {}\"\n".format(label_info["latex"]))
                    ppl.write("set xlabel \"{0}\"\n".format(abscissa_info[1]))

                    # Set axis limits
                    ppl.write("set yrange [{}:{}]\n".format(-2 * label_info["offset_max"],
                                                            2 * label_info["offset_max"]))

                    if abscissa_info[2]:
                        ppl.write("set log x\n")

                    if self.common_x_limits is not None:
                        ppl.write("set xrange [{}:{}]\n".format(self.common_x_limits[0], self.common_x_limits[1]))

                    ppl.write("plot {}\n".format(",".join(plot_items)))

                    ppl.write("""
                    
                    set term eps ; set output '{0}.eps' ; set display ; refresh
                    set term png ; set output '{0}.png' ; set display ; refresh
                    set term pdf ; set output '{0}.pdf' ; set display ; refresh
                    
                    """.format(stem))
                os.system("pyxplot {}.ppl".format(stem))


def generate_set_of_plots(data_sets, abscissa_label, assume_scaled_solar,
                          compare_against_reference_labels, output_figure_stem, run_title, date_stamp=True,
                          abundances_over_h=True):
    """
Create a set of plots of a number of Cannon runs.

    :param data_sets:
    A list of runs of the Cannon which are to be plotted. This should be a list of dictionaries. Each dictionary should
    have the entries:

    cannon_output: The filename of the JSON output file from the Cannon.
    title: Legend caption to use for each Cannon run.
    filters: A string containing semicolon-separated set of constraints on stars we are to include.
    colour: The colour to plot the dataset in.
    line_type: The Pyxplot line type to use for this Cannon run.


    :param abscissa_label:
    The name of the label we are to plot on the horizontal axis. This should be 'SNR/A', 'SNR/pixel', 'ebv'. See
    PlotLabelPrecision::abscissa_labels above, where these are defined.

    :param plot_width:
    The physical width of each graph in cm.

    :param compare_against_reference_labels:
    If true, we measure the difference between each label value estimated by the Cannon and the target value taken from
    that star's metadata in the original spectrum library. I.e. the value used to synthesise the spectrum.

    If false, we measure the deviation from the value for each label estimated at the highest abscissa value -- e.g.
    highest SNR.

    :param output_figure_stem:
    Directory to save plots in.

    :param run_title:
    A suffix to put at the end of the label in the top-left corner of each plot

    :param date_stamp:
    Put a date stamp listing who created each plot, when

    :param abundances_over_h:
    Flag to select whether we plot abundances over H or Fe.

    :return:
    None
    """

    label_info = LabelInformation().label_info

    abscissa_info = AbcissaInformation().abscissa_labels

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

        plotter.add_data_set(cannon_stars=test_items_output,
                             cannon_json=data,
                             label_reference_values=data_set['reference_values'],
                             colour=data_set['colour'],
                             line_type=data_set['line_type'],
                             legend_label=legend_label
                             )
        del data

    plotter.make_plots()


if __name__ == "__main__":

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cannon-output', action="append", dest='cannon_output',
                        help="JSON structure containing the label values estimated by the Cannon.")
    parser.add_argument('--abscissa', default="SNR/A", dest='abscissa_label',
                        help="Name of the quantity to plot on the horizontal axis. Must be a keyword of the "
                             "dictionary abscissa_labels.")
    parser.add_argument('--dataset-label', action="append", dest='data_set_label',
                        help="Title for a set of predictions output from the Cannon, e.g. LRS or HRS.")
    parser.add_argument('--dataset-filter', action="append", dest='data_set_filter',
                        help="A list of semi-colon-separated label constraints on the target label values.")
    parser.add_argument('--dataset-colour', action="append", dest='data_set_colour',
                        help="A list of colours with which to plot each run of the Cannon.")
    parser.add_argument('--dataset-line-type', action="append", dest='data_set_line_type',
                        help="A list of Pyxplot line types with which to plot Cannon runs.")
    parser.add_argument('--output', default="/tmp/cannon_performance_plot", dest='output_file',
                        help="Data file to write output to.")
    parser.add_argument('--assume-scaled-solar',
                        action='store_true',
                        dest="assume_scaled_solar",
                        help="Assume scaled solar abundances for test stars which don't have abundances individually "
                             "specified. This will match what was assumed when synthesising spectra with incomplete "
                             "abundances, but may not lead to very physically plausible parameter distributions.")
    parser.add_argument('--no-assume-scaled-solar',
                        action='store_false',
                        dest="assume_scaled_solar",
                        help="Do not assume scaled solar abundances; do not test whether the Cannon reproduces scaled "
                             "solar abundances for abundances which have missing values.")
    parser.set_defaults(assume_scaled_solar=False)
    parser.add_argument('--use-reference-labels',
                        action='store_true',
                        dest="use_reference_labels",
                        help="Compare the output of the Cannon against a set of reference label values.")
    parser.add_argument('--no-use-reference-labels',
                        action='store_false',
                        dest="use_reference_labels",
                        help="Compare the output of the Cannon against what it produced at the highest abscissa value "
                             "available.")
    parser.set_defaults(use_reference_labels=True)
    parser.add_argument('--abundances-over-h',
                        action='store_true',
                        dest="abundances_over_h",
                        help="Plot abundances over H.")
    parser.add_argument('--abundances-over-fe',
                        action='store_false',
                        dest="abundances_over_h",
                        help="Plot abundances over Fe.")
    parser.set_defaults(abundances_over_h=True)
    args = parser.parse_args()

    # If titles are not supplied for Cannon runs, we use the descriptions stored in the JSON files
    if (args.data_set_label is None) or (len(args.data_set_label) == 0):
        args.data_set_label = [None for i in args.cannon_output]

    # If we have not been supplied with filter constraints to specify which stars to use from each test set, create a
    # blank constraint to allow all stars through.
    if (args.data_set_filter is None) or (len(args.data_set_filter) == 0):
        args.data_set_filter = ["" for i in args.cannon_output]

    # If colours have not been specified for each data set, use a list of default colours
    if (args.data_set_colour is None) or (len(args.data_set_colour) == 0):
        colour_list = ("red", "blue", "orange", "green")
        args.data_set_colour = [colour_list[i % len(colour_list)] for i in range(len(args.cannon_output))]

    # If a line type has not been specified for each data set, use a solid line for everything
    if (args.data_set_line_type is None) or (len(args.data_set_line_type) == 0):
        args.data_set_line_type = [1 for i in args.cannon_output]

    # Check that we have a matching number of labels and sets of Cannon output
    assert len(args.cannon_output) == len(args.data_set_label), \
        "Must have a matching number of libraries and data set labels."

    assert len(args.cannon_output) == len(args.data_set_filter), \
        "Must have a matching number of libraries and data set filters."

    assert len(args.cannon_output) == len(args.data_set_colour), \
        "Must have a matching number of libraries and data set colours."

    assert len(args.cannon_output) == len(args.data_set_linetype), \
        "Must have a matching number of libraries and data set line types."

    # Assemble list of input Cannon output data files
    cannon_outputs = []
    for cannon_output, data_set_label, data_set_filter, data_set_colour, data_set_line_type in \
            zip(args.cannon_output,
                args.data_set_label,
                args.data_set_filter,
                args.data_set_colour,
                args.data_set_line_type):

        # Read the JSON file which we dumped after running the Cannon
        if not os.path.exists(cannon_output):
            print "mean_performance_vs_label.py could not proceed: Cannon run <{}> not found".format(cannon_output)
            sys.exit()

        # Append to list of Cannon data sets
        cannon_outputs.append({'cannon_output': cannon_output,
                               'title': data_set_label,
                               'filters': data_set_filter,
                               'colour': data_set_colour,
                               'line_type': data_set_line_type
                               })

    generate_set_of_plots(data_sets=cannon_outputs,
                          abundances_over_h=args.abundances_over_h,
                          assume_scaled_solar=args.assume_scaled_solar,
                          abscissa_label=args.abscissa_label,
                          compare_against_reference_labels=args.use_reference_labels,
                          output_figure_stem=args.output_file,
                          run_title="",  # "External" if args.use_reference_labels else "Internal"
                          )
