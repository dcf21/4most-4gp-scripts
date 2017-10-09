#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plot results of testing the Cannon against noisy test spectra, to see how well it reproduces stellar labels.
"""

import os
from os import path as os_path
from operator import itemgetter
import argparse
import numpy as np
import json


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

        self.latex_labels = {
            "Teff": (r"$T_{\rm eff}$ $[{\rm K}]$", 0, 350, [100]),
            "logg": (r"$\log{g}$ $[{\rm dex}]$", 0, 1, [0.3]),
            "[Fe/H]": (r"$[{\rm Fe}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[C/H]": (r"$[{\rm C}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[N/H]": (r"$[{\rm N}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[O/H]": (r"$[{\rm O}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Na/H]": (r"$[{\rm Na}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Mg/H]": (r"$[{\rm Mg}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Al/H]": (r"$[{\rm Al}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Si/H]": (r"$[{\rm Si}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Ca/H]": (r"$[{\rm Ca}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Ti/H]": (r"$[{\rm Ti}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Mn/H]": (r"$[{\rm Mn}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Co/H]": (r"$[{\rm Co}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Ni/H]": (r"$[{\rm Ni}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Ba/H]": (r"$[{\rm Ba}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
            "[Sr/H]": (r"$[{\rm Sr}/{\rm H}]$ $[{\rm dex}]$", 0, 1.1, [0.1, 0.2]),
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
                     colour="red",
                     pixels_per_angstrom=1.0,
                     metric=np.std):
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

        :param pixels_per_angstrom:
            The number of pixels per angstrom in the spectrum. Used to convert SNR per pixel into SNR per A.

        :param metric:
            The metric used to convert a list of absolute offsets into an average offset.

        :return:
            None
        """

        self.datasets.append(legend_label)

        # LaTeX strings to use to label each stellar label on graph axes
        latex_labels = [self.latex_labels.get(ln, ln) for ln in self.label_names]

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
                    "{}{:d}_{:d}_{:06.1f}.dat".format(
                        self.output_figure_stem, i, self.data_set_counter, snr_per_a)
                ]

            # Output table of statistical measures of label-mismatch-distribution as a function of SNR (first column)
            np.savetxt("{}{:d}_{:d}.dat".format(self.output_figure_stem, i, self.data_set_counter), y)

            self.plot_precision[i].append("\"{}{:d}_{:d}.dat\" using 1:2 title \"{}\" "
                                          "with lp pt 17 col {}".format(self.output_figure_stem,
                                                                        i, self.data_set_counter,
                                                                        legend_label,
                                                                        colour))

            self.plot_box_whiskers[i][self.data_set_counter] = [
                "\"{0}{1:d}_{2:d}.dat\" using 1:5:3:7 with yerrorrange col black".format(
                    self.output_figure_stem, i, self.data_set_counter)
            ]

            for target_value in latex_label[3]:
                self.plot_precision[i].append("{} with lines col grey(0.75) notitle".format(target_value))

            with open("{}{:d}_{:d}_cracktastic.dat".format(self.output_figure_stem, i, self.data_set_counter),
                      "w") as f:
                for j, datum in enumerate(y):
                    w = 2
                    f.write("{} {}\n".format(datum[0] - w, datum[3]))
                    f.write("{} {}\n".format(datum[0] - w, datum[5]))
                    f.write("{} {}\n".format(datum[0] + w, datum[5]))
                    f.write("{} {}\n\n\n".format(datum[0] + w, datum[3]))

                    self.plot_box_whiskers[i][self.data_set_counter].insert(0,
                                                                            "\"{0}{1:d}_{2:d}_cracktastic.dat\" using 1:2  with filledregion fc red col black lw 0.5 index {3}".format(
                                                                                self.output_figure_stem, i,
                                                                                self.data_set_counter, j))

    def make_plots(self):

        # LaTeX strings to use to label each stellar label on graph axes
        latex_labels = [self.latex_labels.get(ln, ln) for ln in self.label_names]

        for i, (label_name, latex_label) in enumerate(zip(self.label_names, latex_labels)):
            # Create a new pyxplot script for precision plots
            stem = "{}precision_{:d}".format(self.output_figure_stem, i)
            with open("{}.ppl".format(stem), "w") as ppl:
                ppl.write("""
                
                set width 14
                set key top right
                set nodisplay
                set label 1 "{}" graph 1.5, graph 8
                
                """.format(latex_label[0]))

                ppl.write("set ylabel \"{}\"\n".format(latex_label[0]))
                ppl.write("set xlabel \"$S/N$ $[{\\rm \\AA}^{-1}]$\"\n")

                # Set axis limits
                ppl.write("set yrange [{}:{}]\n".format(latex_label[1], latex_label[2]))

                # Set axis ticks
                ppl.write("set xtics (0, 10, 20, 30, 40, 50, 100, 200)\n")

                if self.common_x_limits is not None:
                    ppl.write("set xrange [{}:{}]\n".format(self.common_x_limits[0], self.common_x_limits[1]))

                ppl.write("plot {}\n".format(",".join(self.plot_precision[i])))

                ppl.write("""
                
                set term eps ; set output '{0}.eps' ; set display ; refresh
                set term png ; set output '{0}.png' ; set display ; refresh
                set term pdf ; set output "{0}.pdf" ; set display ; refresh

                """.format(stem))
                ppl.close()
                os.system("pyxplot {}.ppl".format(stem))

            # Create a new pyxplot script for box and whisker plots
            for data_set_counter, plot_items in enumerate(self.plot_box_whiskers[i]):
                stem = "{}whiskers_{:d}_{:d}".format(self.output_figure_stem, i, data_set_counter)
                with open("{}.ppl".format(stem), "w") as ppl:
                    ppl.write("""
                    
                    set width 14
                    set nokey
                    set nodisplay
                    set label 1 "{0}; {1}" graph 1.5, graph 8
                    
                    """.format(latex_label[0], self.datasets[data_set_counter]))

                    ppl.write("set ylabel \"$\Delta$ {}\"\n".format(latex_label[0]))
                    ppl.write("set xlabel \"$S/N$ $[{\\rm \\AA}^{-1}]$\"\n")

                    # Set axis limits
                    ppl.write("set yrange [{}:{}]\n".format(-2 * latex_label[2], 2 * latex_label[2]))

                    # Set axis ticks
                    ppl.write("set xtics (0, 10, 20, 30, 40, 50, 100, 200)\n")

                    if self.common_x_limits is not None:
                        ppl.write("set xrange [{}:{}]\n".format(self.common_x_limits[0], self.common_x_limits[1]))

                    ppl.write("plot {}\n".format(",".join(plot_items)))

                    ppl.write("""
                    
                    set term eps ; set output '{0}.eps' ; set display ; refresh
                    set term png ; set output '{0}.png' ; set display ; refresh
                    set term pdf ; set output "{0}.pdf" ; set display ; refresh
                    
                    """.format(stem))
                    ppl.close()
                    os.system("pyxplot {}.ppl".format(stem))

            # Create a new pyxplot script for histogram plots
            for data_set_counter, data_set_items in enumerate(self.plot_histograms[i]):
                for snr, plot_items in data_set_items.iteritems():
                    stem = "{}histogram_{:d}_{:d}_{:06.1f}".format(self.output_figure_stem, i, data_set_counter, snr)
                    with open("{}.ppl".format(stem), "w") as ppl:
                        ppl.write("""
                    
                    set width 14
                    set nokey
                    set nodisplay
                    set binwidth {0}
                    set label 1 "{1}; {2}; SNR {3:.1f}" graph 1.5, graph 8
                    
                    """.format(latex_label[2] / 25, latex_label[0], self.datasets[data_set_counter], snr))

                        ppl.write("set xlabel \"$\Delta$ {}\"\n".format(latex_label[0]))
                        ppl.write("set xrange [{}:{}]\n".format(-latex_label[2] * 3, latex_label[2] * 3))
                        for j, plot_item in enumerate(plot_items):
                            ppl.write("histogram f_{:d}() \"{}\"\n".format(j, plot_item))
                            ppl.write("plot f_{:d}(x) with boxes fc red\n".format(j))

                        ppl.write("""
                    
                    set term eps ; set output '{0}.eps' ; set display ; refresh
                    set term png ; set output '{0}.png' ; set display ; refresh
                    set term pdf ; set output "{0}.pdf" ; set display ; refresh
                    
                    """.format(stem))
                        ppl.close()
                        os.system("timeout 10s pyxplot {0}.ppl".format(stem))


def generate_set_of_plots(data_sets, compare_against_reference_labels, output_figure_stem, run_title):
    # Work out list of labels to plot, based on first data set we're provided with
    label_names = data_sets[0]['cannon_output']['labels']

    # List of colours
    colour_list = ("red", "blue", "orange", "green")

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
                    reference_values[label] = reference_run["target_{}".format(label)]
                else:
                    # Use the values produced by the Cannon at the highest SNR as the target values for each star
                    reference_values[label] = reference_run[label]
            data_set['reference_values'][star_name] = reference_values

        # Filter only those stars with metallicities >= -0.5
        stars = [item for item in stars if item["[Fe/H]"] >= -0.5]

        # Pick a colour for this data set
        colour = colour_list[counter % len(colour_list)]

        # Convert SNR/pixel to SNR/A at 6000A
        raster = np.array(data_set['cannon_output']['wavelength_raster'])
        raster_diff = np.diff(raster[raster > 6000])
        pixels_per_angstrom = 1.0 / raster_diff[0]

        # Add data set to plot
        plotter.add_data_set(cannon_output=stars,
                             label_reference_values=data_set['reference_values'],
                             colour=colour,
                             legend_label="{} ({})".format(data_set['title'], run_title),
                             pixels_per_angstrom=pixels_per_angstrom
                             )

    plotter.make_plots()


if __name__ == "__main__":

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cannon-output', required=True, action="append", dest='cannon_output',
                        help="JSON structure containing the label values estimated by the Cannon.")
    parser.add_argument('--dataset-label', required=True, action="append", dest='data_set_label',
                        help="Title for a set of predictions output from the Cannon, e.g. LRS or HRS.")
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

    # Check that we have a matching number of labels and sets of Cannon output
    assert len(args.cannon_output) == len(args.data_set_label), \
        "Must have a matching number of libraries and data set labels."

    # Assemble list of input Cannon output data files
    cannon_outputs = []
    for cannon_output, data_set_label in zip(args.cannon_output, args.data_set_label):
        # Append to list of Cannon data sets
        cannon_outputs.append({'cannon_output': json.loads(open(cannon_output).read()),
                               'title': data_set_label})

    generate_set_of_plots(data_sets=cannon_outputs,
                          compare_against_reference_labels=args.use_reference_labels,
                          output_figure_stem=args.output_file,
                          run_title="External" if args.use_reference_labels else "Internal"
                          )
