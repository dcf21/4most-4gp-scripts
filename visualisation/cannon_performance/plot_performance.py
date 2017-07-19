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
from astropy.table import Table

from fourgp_speclib import SpectrumLibrarySqlite


# Convenience function, coz it would've been too helpful for astropy to actually provide dictionary access to rows
def astropy_row_to_dict(x):
    return dict([(i, x[i]) for i in x.columns])


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
                 common_x_limits=None,
                 output_figure_stem="/tmp/cannon_performance"):
        """

        :param label_names:
            A tuple containing the names of the labels we are to plot the precision for.

        :param common_x_limits:
            A two-length tuple containing the lower and upper limits to set on all
            x axes.

        :param output_figure_stem:
            The file path and filename stem where we are to save plots, pyxplot scripts and data files.
        """

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

        self.label_names = label_names
        self.common_x_limits = common_x_limits
        self.output_figure_stem = os_path.abspath(output_figure_stem)
        self.data_set_counter = 0
        self.plot_items = [[] for i in label_names]

    def set_latex_label(self, label, latex, axis_min=0, axis_max=1.1):
        self.latex_labels[label] = (latex, axis_min, axis_max)

    def add_data_set(self, cannon_output, label_reference_values,
                     legend_label=None,
                     colour="red",
                     star_id_column="Starname",
                     snr_column="SNR",
                     pixels_per_angstrom=1.0,
                     metric=np.std):
        """
        Add a data set to a set of precision plots.

        :param cannon_output:
            An astropy Table object containing the label values output by the Cannon.

        :param label_reference_values:
            An astropy Table object containing reference values for the labels for each star.

        :param legend_label:
            The label which should appear in the figure legend for this data set.

        :param colour:
            The colour of this data set. Should be specified as a valid Pyxplot string describing a colour object.

        :param star_id_column:
            The name of the column of cannon_output which identifies each star individually.

        :param snr_column:
            The name of the column in cannon_output which identifies the SNR.

        :param pixels_per_angstrom:
            The number of pixels per angstrom in the spectrum. Used to convert SNR per pixel into SNR per A.

        :param metric:
            The metric used to convert a list of absolute offsets into an average offset.

        :return:
            None
        """

        # LaTeX strings to use to label each stellar label on graph axes
        latex_labels = [self.latex_labels.get(ln, ln) for ln in self.label_names]

        # Create a sorted list of all the SNR values we've got
        snr_values = np.sort(np.unique(cannon_output[snr_column]))

        # Construct the dictionary for storing the Cannon's mismatch to each stellar label
        # label_offset[snr][label_name][reference_value_set_counter] = offset
        label_offset = {}
        for snr in snr_values:
            label_offset[snr] = {}
            for label_name in self.label_names:
                label_offset[snr][label_name] = []

        # Sort Cannon's output by the star it was trying to fit
        cannon_output = cannon_output.group_by(star_id_column)
        group_indices = cannon_output.groups.indices

        # Loop over stars in the Cannon output
        for i, si in enumerate(group_indices[:-1]):
            ei = group_indices[i + 1]

            # Filter the reference labels down to the set which matches the star we're looking at
            star_name = cannon_output[star_id_column][si]

            # Loop over the Cannon's various attempts to match this star (e.g. at different SNR values)
            for result in cannon_output[si:ei]:
                # Loop over the labels the Cannon tried to match
                for label_name in self.label_names:
                    # Fetch the reference value for this label
                    try:
                        ref = label_reference_values[star_name][label_name]

                    except KeyError:
                        ref = np.nan

                    # Calculate the offset of the Cannon's output from the reference value
                    label_offset[result[snr_column]][label_name].append(result[label_name] - ref)

        self.data_set_counter += 1
        for i, (label_name, latex_label) in enumerate(zip(self.label_names, latex_labels)):

            y = np.nan * np.ones_like(snr_values)
            for k, xk in enumerate(snr_values):
                diffs = label_offset[xk][label_name]
                y[k] = metric(diffs)

            scale = np.sqrt(pixels_per_angstrom)

            np.savetxt("{}_{:d}_{:d}.dat".format(self.output_figure_stem, i, self.data_set_counter),
                       np.transpose([snr_values * scale, y]))

            self.plot_items[i].append("\"{}_{:d}_{:d}.dat\" title \"{}\" "
                                      "with lp pt 17 col {}".format(self.output_figure_stem,
                                                                    i, self.data_set_counter,
                                                                    legend_label,
                                                                    colour))

            for target_value in latex_label[3]:
                self.plot_items[i].append("{} with lines col grey(0.75) notitle".format(target_value))

    def make_plots(self, snr_per_angstrom):

        # LaTeX strings to use to label each stellar label on graph axes
        latex_labels = [self.latex_labels.get(ln, ln) for ln in self.label_names]

        for i, (label_name, latex_label) in enumerate(zip(self.label_names, latex_labels)):
            # Create a new pyxplot script
            with open("{}_{:d}.ppl".format(self.output_figure_stem, i), "w") as ppl:
                ppl.write("""
                set width 14
                set key top right
                set nodisplay
                set label 1 "{}" graph 1.5, graph 8
                """.format(latex_label[0]))

                ppl.write("set ylabel \"{}\"\n".format(latex_label[0]))

                if snr_per_angstrom:
                    ppl.write("set xlabel \"$S/N$ $[{\\rm \\AA}^{-1}]$\"\n")
                else:
                    ppl.write("set xlabel \"$S/N$ $[{\\rm pixel}^{-1}]$\"\n")

                # Set axis limits
                ppl.write("set yrange [{}:{}]\n".format(latex_label[1], latex_label[2]))

                # Set axis ticks
                ppl.write("set xtics (0, 10, 20, 30, 40, 50, 100, 200)\n")

                if self.common_x_limits is not None:
                    ppl.write("set xrange [{}:{}]\n".format(self.common_x_limits[0], self.common_x_limits[1]))

                ppl.write("plot {}\n".format(",".join(self.plot_items[i])))

                ppl.write("""
                set term eps ; set output '{}_{:d}.eps' ; set display ; refresh
                set term png ; set output '{}_{:d}.png' ; set display ; refresh\n
                """.format(self.output_figure_stem, i, self.output_figure_stem, i))
                ppl.close()
                os.system("pyxplot {}_{:d}.ppl".format(self.output_figure_stem, i))


def generate_set_of_plots(data_sets, compare_against_reference_labels, output_figure_stem, run_title):
    # List of labels to plot
    label_names = ("Teff", "logg", "[Fe/H]",
                   "[C/H]", "[N/H]", "[O/H]", "[Na/H]", "[Mg/H]", "[Al/H]", "[Si/H]",
                   "[Ca/H]", "[Ti/H]", "[Mn/H]", "[Co/H]", "[Ni/H]", "[Ba/H]", "[Sr/H]")
    # n_labels = len(label_names)

    # List of colours
    colour_list = ("red", "blue", "orange", "green")

    # Instantiate plotter
    plotter = PlotLabelPrecision(label_names=label_names,
                                 common_x_limits=(0, 250),
                                 output_figure_stem=output_figure_stem)

    # Loop over the various Cannon runs we have, e.g. LRS and HRS
    for counter, data_set in enumerate(data_sets):
        # Fetch wavelength raster for each data set
        data_set['spectrum_ids'] = [i['specId'] for i in data_set['spectrum_library'].search()]
        data_set['spectrum_ids'].sort()
        data_set['spectrum_first'] = data_set['spectrum_library'].open(ids=data_set['spectrum_ids'][0])
        data_set['wavelength_raster'] = data_set['spectrum_first'].wavelengths

        # Fetch Cannon output
        data_set['cannon_data'] = Table.read(data_set['cannon_output'], format='ascii')
        data_set['cannon_data_dicts'] = [astropy_row_to_dict(item) for item in data_set['cannon_data']]

        # Fetch reference values
        if compare_against_reference_labels:
            # Look up reference values in the metadata in the SpectrumLibrary that the Cannon was trying to fit
            data_set['metadata'] = data_set['spectrum_library'].get_metadata(ids=data_set['spectrum_ids'])
            data_set['reference_values'] = {}
            for item in data_set['metadata']:
                star_name = item['Starname']
                reference_values = dict([[label, item[label] if label in item else np.nan]
                                         for label in label_names])
                data_set['reference_values'][star_name] = reference_values
        else:
            # Use the values produced by the Cannon at the highest SNR as the target values for each star
            star_names = [item['Starname'] for item in data_set['cannon_data_dicts']]
            star_names_distinct = set(star_names)

            # Loop over all the stars the Cannon tried to fit
            for star_name in star_names_distinct:
                # Create a list of all the available SNRs for this star
                snr_list = [(index, data_set['cannon_data_dicts'][index]['SNR'])
                            for index in range(len(data_set['cannon_data_dicts']))
                            if data_set['cannon_data_dicts'][index]['Starname'] == star_name
                            ]
                # Sort the list into order of ascending SNR
                snr_list.sort(key=itemgetter(1))

                reference_run = data_set['cannon_data_dicts'][snr_list[-1][0]]
                reference_values = dict([[label, reference_run[label] if label in reference_run else np.nan]
                                         for label in label_names])
                data_set['reference_values'][star_name] = reference_values

        # Filter only those stars with metallicities >= -0.5
        metal_rich = data_set['cannon_data']["[Fe/H]"] >= -0.5
        data_set['cannon_data_filtered'] = data_set['cannon_data'][metal_rich]

        # Pick a colour for this data set
        colour = colour_list[counter % len(colour_list)]

        # Add data set to plot
        plotter.add_data_set(data_set['cannon_data_filtered'],
                             label_reference_values=data_set['reference_values'],
                             colour=colour,
                             legend_label="{} ({})".format(data_set['title'], run_title),
                             pixels_per_angstrom=np.median(1.0 / np.diff(data_set['wavelength_raster'])))

    plotter.make_plots(snr_per_angstrom=True)


if __name__ == "__main__":

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', required=True, action="append", dest='spectrum_libraries',
                        help="Library of spectra that the Cannon tried to fit.")
    parser.add_argument('--cannon-output', required=True, action="append", dest='cannon_output',
                        help="ASCII table containing the label values estimated by the Cannon.")
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

    # Check that we have a matching number of libraries and sets of Cannon output
    assert len(args.spectrum_libraries) == len(args.cannon_output), \
        "Must have a matching number of libraries and sets of Cannon output."
    assert len(args.spectrum_libraries) == len(args.data_set_label), \
        "Must have a matching number of libraries and data set labels."

    # Set path to workspace where we expect to find libraries of spectra
    our_path = os_path.split(os_path.abspath(__file__))[0]
    workspace = os_path.join(our_path, "..", "..", "workspace")

    # Assemble list of input SpectrumLibraries with list of Cannon output data
    cannon_outputs = []
    for spectrum_library, cannon_output, data_set_label in \
            zip(args.spectrum_libraries, args.cannon_output, args.data_set_label):
        # Open training set
        training_library_path = os_path.join(workspace, spectrum_library)
        training_library = SpectrumLibrarySqlite(path=training_library_path, create=False)

        # Append to list of Cannon data sets
        cannon_outputs.append({'spectrum_library': training_library,
                               'cannon_output': cannon_output,
                               'title': data_set_label})

    generate_set_of_plots(data_sets=cannon_outputs,
                          compare_against_reference_labels=args.use_reference_labels,
                          output_figure_stem=args.output_file,
                          run_title="External" if args.use_reference_labels else "Internal"
                          )
