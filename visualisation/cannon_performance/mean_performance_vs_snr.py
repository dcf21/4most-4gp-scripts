#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plot results of testing the Cannon against noisy test spectra, to see how well it reproduces stellar labels.
"""

import os
from os import path as os_path
import re
from operator import itemgetter
import argparse
import numpy as np
import json

from lib_multiplotter import make_multiplot


class PlotLabelPrecision:
    """
    Class for making a plot of the Cannon's performance.

    :ivar latex_labels:
        A tuple containing LaTeX labels to use on the figure axes.

    :ivar plot_counter:
        An integer counter used to give plots for each stellar label a unique filename.
    """

    def __init__(self,
                 label_names,
                 number_data_sets,
                 common_x_limits=None,
                 output_figure_stem="/tmp/cannon_performance/"):
        """

        :param label_names:
            A tuple containing the names of the labels we are to plot the precision for.

        :param common_x_limits:
            A two-length tuple containing the lower and upper limits to set on all
            x axes.

        :param output_figure_stem:
            The file path where we are to save plots, pyxplot scripts and data files.
        """

        # Create directory to store output files in
        os.system("mkdir -p {}".format(output_figure_stem))
        os.system("rm -f {}/*".format(output_figure_stem))

        # ( LaTeX title , minimum offset , maximum offset , 4MOST target accuracy )
        self.latex_labels = {
            "Teff": (r"$T_{\rm eff}$ $[{\rm K}]$", 0, 300, [100]),
            "logg": (r"$\log{g}$ $[{\rm dex}]$", 0, 0.8, [0.3]),
            "[Fe/H]": (r"$[{\rm Fe}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[C/H]": (r"$[{\rm C}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[N/H]": (r"$[{\rm N}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[O/H]": (r"$[{\rm O}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Na/H]": (r"$[{\rm Na}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Mg/H]": (r"$[{\rm Mg}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Al/H]": (r"$[{\rm Al}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Si/H]": (r"$[{\rm Si}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Ca/H]": (r"$[{\rm Ca}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Ti/H]": (r"$[{\rm Ti}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Mn/H]": (r"$[{\rm Mn}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Co/H]": (r"$[{\rm Co}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Ni/H]": (r"$[{\rm Ni}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Ba/H]": (r"$[{\rm Ba}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Sr/H]": (r"$[{\rm Sr}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Cr/H]": (r"$[{\rm Cr}/{\rm H}]$ $[{\rm dex}]$", 0, 0.75, [0.1, 0.2]),
            "[Li/H]": (r"$[{\rm Li}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.2, 0.4]),
            "[Eu/H]": (r"$[{\rm Eu}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.2, 0.4]),
        }

        self.datasets = []
        self.label_names = label_names
        self.number_data_sets = number_data_sets
        self.common_x_limits = common_x_limits
        self.output_figure_stem = os_path.abspath(output_figure_stem) + "/"
        self.data_set_counter = -1
        self.plot_precision = [[] for i in label_names]
        self.plot_box_whiskers = [[[] for j in range(number_data_sets)] for i in label_names]
        self.plot_histograms = [[{} for j in range(number_data_sets)] for i in label_names]

    def set_latex_label(self, label, latex, axis_min=0, axis_max=1.1):
        self.latex_labels[label] = (latex, axis_min, axis_max)

    def add_data_set(self, cannon_output, label_reference_values,
                     legend_label=None,
                     colour="red", line_type=1,
                     pixels_per_angstrom=1.0,
                     metric=lambda x: np.sqrt(np.mean(np.square(x)))
                     ):
        """
        Add a data set to a set of precision plots.

        :param cannon_output:
            An list of dictionaries containing the label values output by the Cannon.

        :param label_reference_values:
            A dictionary of dictionaries containing reference values for the labels for each star.

        :param legend_label:
            The label which should appear in the figure legend for this data set.

        :param colour:
            The colour of this data set. Should be specified as a valid Pyxplot string describing a colour object.

        :param line_type:
            The Pyxplot line type to use for this data set. Should be specified as an integer.

        :param pixels_per_angstrom:
            The number of pixels per angstrom in the spectrum. Used to convert SNR per pixel into SNR per A.

        :param metric:
            The metric used to convert a list of absolute offsets into an average offset.

        :return:
            None
        """

        self.datasets.append(legend_label)

        # LaTeX strings to use to label each stellar label on graph axes
        latex_labels = [self.latex_labels[ln] for ln in self.label_names]

        # Create a sorted list of all the SNR values we've got
        snr_values = [item['SNR'] for item in cannon_output]
        snr_values = sorted(set(snr_values))

        # Create a sorted list of all the stars we've got
        star_names = [item['Starname'] for item in cannon_output]
        star_names = sorted(set(star_names))

        # Construct the dictionary for storing the Cannon's mismatch to each stellar label
        # label_offset[snr][label_name][reference_value_set_counter] = offset
        label_offset = {}
        for snr in snr_values:
            label_offset[snr] = {}
            for label_name in self.label_names:
                label_offset[snr][label_name] = []

        # Loop over stars in the Cannon output
        for star_name in star_names:
            # Loop over the Cannon's various attempts to match this star (e.g. at different SNR values)
            for star in cannon_output:
                if star['Starname'] == star_name:
                    # Loop over the labels the Cannon tried to match
                    for label_name in self.label_names:
                        # Fetch the reference value for this label
                        try:
                            ref = label_reference_values[star_name][label_name]
                        except KeyError:
                            ref = np.nan

                        # Calculate the offset of the Cannon's output from the reference value
                        label_offset[star['SNR']][label_name].append(star[label_name] - ref)

        self.data_set_counter += 1

        # Extract list of label offsets for each label, and for each SNR
        for i, (label_name, latex_label) in enumerate(zip(self.label_names, latex_labels)):
            scale = np.sqrt(pixels_per_angstrom)

            y = []
            for k, xk in enumerate(snr_values):
                snr_per_a = xk * scale

                # List of offsets
                diffs = label_offset[xk][label_name]

                # Sort list
                diffs.sort()

                def percentile(fraction):
                    return diffs[int(fraction / 100. * len(diffs))]

                y.append([])
                y[-1].extend([snr_per_a])
                y[-1].extend(
                    [metric(diffs), percentile(5), percentile(25), percentile(50), percentile(75), percentile(95)])

                # Output histogram of label mismatches at this SNR
                np.savetxt(
                    "{}{:d}_{:d}_{:06.1f}.dat".format(self.output_figure_stem, i, self.data_set_counter, snr_per_a),
                    np.transpose(diffs))

                self.plot_histograms[i][self.data_set_counter][snr_per_a] = [
                    ("{}{:d}_{:d}_{:06.1f}.dat".format(self.output_figure_stem, i, self.data_set_counter, snr_per_a),
                     scale
                     )
                ]

            # Output table of statistical measures of label-mismatch-distribution as a function of SNR (first column)
            np.savetxt("{}{:d}_{:d}.dat".format(self.output_figure_stem, i, self.data_set_counter), y)

            self.plot_precision[i].append("\"{}{:d}_{:d}.dat\" using 1:2 title \"{}\" "
                                          "with lp pt 17 col {} lt {:d}".
                                          format(self.output_figure_stem,
                                                 i, self.data_set_counter,
                                                 legend_label,
                                                 colour, int(line_type)))

            self.plot_box_whiskers[i][self.data_set_counter] = [
                "\"{0}{1:d}_{2:d}.dat\" using 1:5:3:7 with yerrorrange col black".format(
                    self.output_figure_stem, i, self.data_set_counter)
            ]

            for target_value in latex_label[3]:
                self.plot_precision[i].append("{} with lines col grey(0.75) notitle".format(target_value))

            with open("{}{:d}_{:d}_cracktastic.dat".format(self.output_figure_stem, i, self.data_set_counter),
                      "w") as f:
                for j, datum in enumerate(y):
                    w = 1.2
                    f.write("{} {}\n".format(datum[0] - w, datum[3]))
                    f.write("{} {}\n".format(datum[0] - w, datum[5]))
                    f.write("{} {}\n".format(datum[0] + w, datum[5]))
                    f.write("{} {}\n\n\n".format(datum[0] + w, datum[3]))

                    self.plot_box_whiskers[i][self.data_set_counter]. \
                        insert(0,
                               "\"{0}{1:d}_{2:d}_cracktastic.dat\" using 1:2 "
                               "with filledregion fc red col black lw 0.5 index {3}".format(
                                   self.output_figure_stem, i,
                                   self.data_set_counter, j))

    def make_plots(self):

        width = 22
        aspect = 1 / 1.618034  # Golden ratio

        # LaTeX strings to use to label each stellar label on graph axes
        latex_labels = [self.latex_labels[ln] for ln in self.label_names]

        # Create a new pyxplot script for precision plots
        eps_files = {
            "precision": [],
            "whiskers": [],
            "histograms": []
        }

        for i, (label_name, latex_label) in enumerate(zip(self.label_names, latex_labels)):
            stem = "{}precision_{:d}".format(self.output_figure_stem, i)
            with open("{}.ppl".format(stem), "w") as ppl:
                ppl.write("""
                
                set width {0}
                set size ratio {1}
                set term dpi 200
                set key top right
                set nodisplay
                set fontsize 1.8
                set label 1 "{2}" page 1, page {3}
                
                """.format(width, aspect, latex_label[0], width * aspect - 0.5))

                ppl.write("set ylabel \"RMS offset in {}\"\n".format(latex_label[0]))
                ppl.write("set xlabel \"$S/N$ $[{\\rm \\AA}^{-1}]$\"\n")

                # Set axis limits
                ppl.write("set yrange [{}:{}]\n".format(latex_label[1], latex_label[2]))

                if self.common_x_limits is not None:
                    ppl.write("set xrange [{}:{}]\n".format(self.common_x_limits[0], self.common_x_limits[1]))

                ppl.write("plot {}\n".format(",".join(self.plot_precision[i])))

                ppl.write("""
                
                set term eps ; set output '{0}.eps' ; set display ; refresh
                set term png ; set output '{0}.png' ; set display ; refresh
                set term pdf ; set output '{0}.pdf' ; set display ; refresh

                """.format(stem))
            os.system("pyxplot {}.ppl".format(stem))
            eps_files["precision"].append("{0}.eps".format(stem))

            # Create a new pyxplot script for box and whisker plots
            for data_set_counter, plot_items in enumerate(self.plot_box_whiskers[i]):
                stem = "{}whiskers_{:d}_{:d}".format(self.output_figure_stem, i, data_set_counter)
                with open("{}.ppl".format(stem), "w") as ppl:
                    ppl.write("""
                
                    set width {0}
                    set size ratio {1}
                    set term dpi 200
                    set nokey
                    set nodisplay
                    set label 1 "{2}; {3}" page 1, page {4}
                    
                    """.format(width, aspect, latex_label[0], self.datasets[data_set_counter], width * aspect - 0.5))

                    ppl.write("set ylabel \"$\Delta$ {}\"\n".format(latex_label[0]))
                    ppl.write("set xlabel \"$S/N$ $[{\\rm \\AA}^{-1}]$\"\n")

                    # Set axis limits
                    ppl.write("set yrange [{}:{}]\n".format(-2 * latex_label[2], 2 * latex_label[2]))

                    if self.common_x_limits is not None:
                        ppl.write("set xrange [{}:{}]\n".format(self.common_x_limits[0], self.common_x_limits[1]))

                    ppl.write("plot {}\n".format(",".join(plot_items)))

                    ppl.write("""
                    
                    set term eps ; set output '{0}.eps' ; set display ; refresh
                    set term png ; set output '{0}.png' ; set display ; refresh
                    set term pdf ; set output '{0}.pdf' ; set display ; refresh
                    
                    """.format(stem))
                os.system("pyxplot {}.ppl".format(stem))
                eps_files["whiskers"].append("{0}.eps".format(stem))

            # Create a new pyxplot script for histogram plots
            for data_set_counter, data_set_items in enumerate(self.plot_histograms[i]):
                stem = "{}histogram_{:d}_{:d}".format(self.output_figure_stem, i, data_set_counter)
                with open("{}.ppl".format(stem), "w") as ppl:
                    ppl.write("""
                
                    set width {0}
                    set size ratio {1}
                    set term dpi 200
                    set key ycentre right
                    set nodisplay
                    set binwidth {2}
                    set label 1 "{3}; {4}" page 1, page {5}
                    
                    col_scale(z) = hsb(0.75 * z, 1, 1)
                    
                    """.format(width, aspect,
                               latex_label[2] / 60.,
                               latex_label[0], self.datasets[data_set_counter], width * aspect - 0.5))

                    ppl.write("set xlabel \"$\Delta$ {}\"\n".format(latex_label[0]))
                    ppl.write("set ylabel \"Number of stars per unit {}\"\n".format(latex_label[0]))
                    ppl.write("set xrange [{}:{}]\n".format(-latex_label[2] * 1.2, latex_label[2] * 1.2))

                    ppl_items = []
                    k_max = float(len(data_set_items) - 1)
                    if k_max < 1:
                        k_max = 1.

                    for k, (snr, plot_items) in enumerate(sorted(data_set_items.iteritems())):
                        for j, (plot_item, snr_scaling) in enumerate(plot_items):
                            ppl.write("histogram f_{0:d}_{1:.0f}() \"{2}\"\n".format(j, snr, plot_item))
                            ppl_items.append("f_{0:d}_{1:.0f}(x) with lines colour col_scale({3}) "
                                             "title 'SNR/A {1:.1f}; SNR/pixel {2:.1f}'".
                                             format(j, snr, snr / snr_scaling, k / k_max))

                    ppl.write("""
                    plot {0}
                    
                    set term eps ; set output '{1}.eps' ; set display ; refresh
                    set term png ; set output '{1}.png' ; set display ; refresh
                    set term pdf ; set output '{1}.pdf' ; set display ; refresh
                    
                    """.format(", ".join(ppl_items), stem))
                os.system("timeout 10s pyxplot {0}.ppl".format(stem))
                eps_files["histograms"].append("{0}.eps".format(stem))

        for name, items in eps_files.iteritems():
            make_multiplot(eps_files=items,
                           output_filename="{}{}_multiplot".format(self.output_figure_stem, name),
                           aspect=6. / 8
                           )


def generate_set_of_plots(data_sets, compare_against_reference_labels, output_figure_stem, run_title):
    # Work out list of labels to plot, based on first data set we're provided with
    label_names = data_sets[0]['cannon_output']['labels']

    # Instantiate plotter
    plotter = PlotLabelPrecision(label_names=label_names,
                                 common_x_limits=(0, 250),
                                 number_data_sets=len(data_sets),
                                 output_figure_stem=output_figure_stem)

    # Loop over the various Cannon runs we have, e.g. LRS and HRS
    for counter, data_set in enumerate(data_sets):

        # Fetch Cannon output
        stars = data_set['cannon_output']['stars']

        # Fetch reference values for each star
        star_names = [item['Starname'] for item in stars]
        star_names_distinct = set(star_names)

        data_set['reference_values'] = {}

        # Loop over all the stars the Cannon tried to fit
        for star_name in star_names_distinct:
            # Create a list of all the available SNRs for this star
            snr_list = [(index, stars[index]['SNR'])
                        for index in range(len(stars))
                        if stars[index]['Starname'] == star_name
                        ]
            # Sort the list into order of ascending SNR
            snr_list.sort(key=itemgetter(1))

            reference_run = stars[snr_list[-1][0]]
            reference_values = {}
            for label in label_names:
                if compare_against_reference_labels:
                    # Use values that were used to synthesise this spectrum
                    key = "target_{}".format(label)
                    if key in reference_run:
                        reference_values[label] = reference_run["target_{}".format(label)]
                    elif "[Fe/H]" in reference_run:
                        reference_values[label] = reference_run["[Fe/H]"]  # Assume scales with [Fe/H]
                    else:
                        reference_values[label] = np.nan
                else:
                    # Use the values produced by the Cannon at the highest SNR as the target values for each star
                    reference_values[label] = reference_run[label]
            data_set['reference_values'][star_name] = reference_values

        # Filter only those stars which meet input criteria
        stars_output = []
        for star in stars:
            star_name = star['Starname']
            reference_values = data_set['reference_values'][star_name]

            meets_filters = True
            for constraint in data_set['filters'].split(";"):
                constraint = constraint.strip()
                if constraint == "":
                    continue
                constraint_label = re.split("<|=|>", constraint)[0]
                constraint_value_string = re.split("<|=|>", constraint)[-1]
                constraint_value = constraint_value_string
                try:
                    constraint_value = float(constraint_value)
                except ValueError:
                    pass
                if constraint == "{}={}".format(constraint_label, constraint_value_string):
                    meets_filters = meets_filters and (reference_values[constraint_label] == constraint_value)
                elif constraint == "{}<={}".format(constraint_label, constraint_value_string):
                    meets_filters = meets_filters and (reference_values[constraint_label] <= constraint_value)
                elif constraint == "{}<{}".format(constraint_label, constraint_value_string):
                    meets_filters = meets_filters and (reference_values[constraint_label] < constraint_value)
                elif constraint == "{}>={}".format(constraint_label, constraint_value_string):
                    meets_filters = meets_filters and (reference_values[constraint_label] >= constraint_value)
                elif constraint == "{}>{}".format(constraint_label, constraint_value_string):
                    meets_filters = meets_filters and (reference_values[constraint_label] > constraint_value)
                else:
                    assert False, "Could not parse constraint <{}>.".format(constraint)
            if meets_filters:
                stars_output.append(star)

        # Convert SNR/pixel to SNR/A at 6000A
        raster = np.array(data_set['cannon_output']['wavelength_raster'])
        raster_diff = np.diff(raster[raster > 6000])
        pixels_per_angstrom = 1.0 / raster_diff[0]

        # Add data set to plot
        plotter.add_data_set(cannon_output=stars_output,
                             label_reference_values=data_set['reference_values'],
                             colour=data_set['colour'],
                             line_type=data_set['line_type'],
                             legend_label="{} ({})".format(data_set['title'], run_title),
                             pixels_per_angstrom=pixels_per_angstrom
                             )

    plotter.make_plots()


if __name__ == "__main__":

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cannon-output', action="append", dest='cannon_output',
                        help="JSON structure containing the label values estimated by the Cannon.")
    parser.add_argument('--dataset-label', action="append", dest='data_set_label',
                        help="Title for a set of predictions output from the Cannon, e.g. LRS or HRS.")
    parser.add_argument('--dataset-filter', action="append", dest='data_set_filter',
                        help="A list of semi-colon-separated label constraints on the target label values.")
    parser.add_argument('--dataset-colour', action="append", dest='data_set_colour',
                        help="A list of colours with which to plot each run of the Cannon.")
    parser.add_argument('--dataset-linetype', action="append", dest='data_set_linetype',
                        help="A list of Pyxplot line types with which to plot Cannon runs.")
    parser.add_argument('--output-file', default="/tmp/cannon_performance_plot", dest='output_file',
                        help="Data file to write output to.")
    parser.add_argument('--use-reference-labels',
                        required=False,
                        action='store_true',
                        dest="use_reference_labels",
                        help="Compare the output of the Cannon against a set of reference label values.")
    parser.add_argument('--no-use-reference-labels',
                        required=False,
                        action='store_false',
                        dest="use_reference_labels",
                        help="Compare the output of the Cannon against what it produced at the highest SNR available.")
    parser.set_defaults(use_reference_labels=True)
    args = parser.parse_args()

    # If titles, colours, etc, are not supplied for Cannon runs, we use the descriptions stored in the JSON files
    if (args.data_set_label is None) or (len(args.data_set_label) == 0):
        args.data_set_label = [None for i in args.cannon_output]

    if (args.data_set_filter is None) or (len(args.data_set_filter) == 0):
        args.data_set_filter = ["" for i in args.cannon_output]

    if (args.data_set_colour is None) or (len(args.data_set_colour) == 0):
        # List of default colours
        colour_list = ("red", "blue", "orange", "green")

        args.data_set_colour = [colour_list[i % len(colour_list)] for i in range(len(args.cannon_output))]

    if (args.data_set_linetype is None) or (len(args.data_set_linetype) == 0):
        args.data_set_linetype = [1 for i in args.cannon_output]

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
                args.data_set_linetype):
        # Read the JSON file which we dumped after running the Cannon
        data = json.loads(open(cannon_output).read())

        # If no label has been specified for this Cannon run, use the description field from the JSON output
        if data_set_label is None:
            data_set_label = data['description']

        # Append to list of Cannon data sets
        cannon_outputs.append({'cannon_output': data,
                               'title': data_set_label,
                               'filters': data_set_filter,
                               'colour': data_set_colour,
                               'line_type': data_set_line_type
                               })

    generate_set_of_plots(data_sets=cannon_outputs,
                          compare_against_reference_labels=args.use_reference_labels,
                          output_figure_stem=args.output_file,
                          run_title="External" if args.use_reference_labels else "Internal"
                          )
