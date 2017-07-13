#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plot results of testing the Cannon against noisy test spectra, to see how well it reproduces stellar labels.
"""

from os import path as os_path
from operator import itemgetter
import argparse
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import Table
from matplotlib.ticker import MaxNLocator

from fourgp_speclib import SpectrumLibrarySqlite


# Convenience function, coz it would've been too helpful for astropy to actually provide dictionary access to rows
def astropy_row_to_dict(x):
    return dict([(i, x[i]) for i in x.columns])


class PlotLabelPrecision:
    """
    Class for making a plot of the Cannon's performance.

    :ivar latex_labels:
        A tuple containing LaTeX labels to use on the figure axes.

    :ivar fig:
        A `matplotlib` figure that has at least as many axes as the
        number of `label_names`.
    """

    def __init__(self):
        self.latex_labels = {
            "Teff": r"$T_{\rm eff}$ $[{\rm K}]$",
            "logg": r"$\log{g}$ $[{\rm dex}]$",
            "[Fe/H]": r"$[{\rm Fe}/{\rm H}]$ $[{\rm dex}]$",
            "[C/H]": r"$[{\rm C}/{\rm H}]$ $[{\rm dex}]$",
            "[N/H]": r"$[{\rm N}/{\rm H}]$ $[{\rm dex}]$",
            "[O/H]": r"$[{\rm O}/{\rm H}]$ $[{\rm dex}]$",
            "[Na/H]": r"$[{\rm Na}/{\rm H}]$ $[{\rm dex}]$",
            "[Mg/H]": r"$[{\rm Mg}/{\rm H}]$ $[{\rm dex}]$",
            "[Al/H]": r"$[{\rm Al}/{\rm H}]$ $[{\rm dex}]$",
            "[Si/H]": r"$[{\rm Si}/{\rm H}]$ $[{\rm dex}]$",
            "[Ca/H]": r"$[{\rm Ca}/{\rm H}]$ $[{\rm dex}]$",
            "[Ti/H]": r"$[{\rm Ti}/{\rm H}]$ $[{\rm dex}]$",
            "[Mn/H]": r"$[{\rm Mn}/{\rm H}]$ $[{\rm dex}]$",
            "[Co/H]": r"$[{\rm Co}/{\rm H}]$ $[{\rm dex}]$",
            "[Ni/H]": r"$[{\rm Ni}/{\rm H}]$ $[{\rm dex}]$",
            "[Ba/H]": r"$[{\rm Ba}/{\rm H}]$ $[{\rm dex}]$",
            "[Sr/H]": r"$[{\rm Sr}/{\rm H}]$ $[{\rm dex}]$",
        }

        self.fig = None

    def set_latex_label(self, label, latex):
        self.latex_labels[label] = latex

    def plot_label_precision(self, cannon_output, label_names, label_reference_values,
                             legend_labels=None,
                             colors=("r", "k"),
                             star_id_column="Starname",
                             snr_column="SNR", pixels_per_angstrom=1.0, common_y_axes=None, n_plots=None,
                             common_x_limits=None, metric=np.std):
        """
        Plot the precision in labels as a function of S/N.

        :param cannon_output:
            A table containing results for stars at many S/N ratios.

        :param label_names:
            A tuple containing the label names.

        :param label_reference_values:
            A list of astropy tables containing the expected labels for each star.

        :param legend_labels: [optional]
            A list-like containing labels that will appear in the legend.

        :param pixels_per_angstrom: [optional]
            The number of pixels per Angstrom. If this is set to anything other than
            1, the S/N on the x-axis will be shown per Angstrom, not per pixel.

        :param common_y_axes: [optional]
            Specify axes indices that should have the same y-axis limits and
            markers.

        :param common_x_limits: [optional]
            A two-length tuple containing the lower and upper limits to set on all
            x axes.

        :returns:
            None
        """

        # LaTeX strings to use to label each stellar label on graph axes
        latex_labels = [self.latex_labels.get(ln, ln) for ln in label_names]

        # Count how many stellar labels we're plotting
        n_labels = len(label_names)

        # Create a sorted list of all the SNR values we've got
        snr_values = np.sort(np.unique(cannon_output[snr_column]))

        # label_reference_values should be a list of `astropy` tables.
        # We plot performance of Cannon relative to each set of reference values provided.
        # If only one astropy table is provided, create a list of length one.
        if not isinstance(label_reference_values, (list, tuple)):
            label_reference_values = [label_reference_values]

        # Construct the dictionary for storing the Cannon's mismatch to each stellar label
        # label_offset[snr][label_name][reference_value_set_counter] = offset
        label_offset = {}
        for snr in snr_values:
            label_offset[snr] = {}
            for label_name in label_names:
                label_offset[snr][label_name] = {}
                for j in range(len(label_reference_values)):
                    label_offset[snr][label_name][j] = []

        # Sort Cannon's output by the star it was trying to fit
        cannon_output = cannon_output.group_by(star_id_column)
        group_indices = cannon_output.groups.indices

        # Loop over stars in the Cannon output
        for i, si in enumerate(group_indices[:-1]):
            ei = group_indices[i + 1]

            # Loop over the sets of reference values that we have
            for j in range(len(label_reference_values)):
                # Get the reference labels
                reference = label_reference_values[j]

                # Filter the reference labels down to the set which matches the star we're looking at
                star_name = cannon_output[star_id_column][si]

                # Loop over the Cannon's various attempts to match this star (e.g. at different SNR values)
                for result in cannon_output[si:ei]:
                    # Loop over the labels the Cannon tried to match
                    for label_name in label_names:
                        # Fetch the reference value for this label
                        try:
                            ref = reference[star_name][label_name]

                        except KeyError:
                            ref = np.nan

                        # Calculate the offset of the Cannon's output from the reference value
                        label_offset[result[snr_column]][label_name][j].append(result[label_name] - ref)

        # If we haven't started building a MatPlotLib figure yet, create it now
        if self.fig is None:
            if n_plots is None:
                n_plots = n_labels
            self.fig, _ = plt.subplots(n_plots, 1, figsize=(6, n_plots * 4))

        for i, (ax, label_name, latex_label) in enumerate(
                zip(np.array(self.fig.axes).flatten(), label_names, latex_labels)):

            for j, color in enumerate(colors):

                legend_label = None if legend_labels is None else legend_labels[j]

                y = np.nan * np.ones_like(snr_values)
                for k, xk in enumerate(snr_values):
                    diffs = label_offset[xk][label_name][j]
                    y[k] = metric(diffs)

                scale = np.sqrt(pixels_per_angstrom)
                ax.plot(snr_values * scale, y, c=color, label=legend_label)
                ax.scatter(snr_values * scale, y, s=100, facecolor=color, zorder=10, alpha=0.75, label=None)

            ax.set_ylabel(latex_label)

            if ax.is_last_row():
                if pixels_per_angstrom != 1:
                    ax.set_xlabel(r"$S/N$ $[{\rm \AA}^{-1}]$")
                else:
                    ax.set_xlabel(r"$S/N$ $[{\rm pixel}^{-1}]$")
            else:
                ax.set_xticklabels([])

            # Set axis limits
            ax.set_ylim(0, ax.get_ylim()[1])
            ax.set_xlim(0, ax.get_xlim()[1])
            ax.yaxis.set_major_locator(MaxNLocator(5))

            # Set axis ticks
            ax.set_xticks([0, 10, 20, 30, 40, 50, 100, 200])

            if common_x_limits is not None:
                ax.set_xlim(common_x_limits)

        if legend_labels is not None:
            self.fig.axes[0].legend(frameon=False)

        if common_y_axes is not None:
            limit = max([ax.get_ylim()[1] for i, ax in enumerate(self.fig.axes) if i in common_y_axes])
            for i, ax in enumerate(self.fig.axes):
                if i not in common_y_axes:
                    continue
                ax.set_ylim(0, limit)

                ax.axhline(0.1, linestyle=":", c="#666666", zorder=-1)
                ax.axhline(0.2, linestyle="--", c="#666666", zorder=-1)

        self.fig.tight_layout()


def generate_set_of_plots(data_sets, compare_against_reference_labels, output_figure, run_title):
    # List of labels to plot
    label_names = ("Teff", "logg", "[Fe/H]",
                   "[C/H]", "[N/H]", "[O/H]", "[Na/H]", "[Mg/H]", "[Al/H]", "[Si/H]",
                   "[Ca/H]", "[Ti/H]", "[Mn/H]", "[Co/H]", "[Ni/H]", "[Ba/H]", "[Sr/H]")
    # n_labels = len(label_names)

    # List of colours
    colour_list = ("#2980b9", "#e67e22")

    # Instantiate plotter
    plotter = PlotLabelPrecision()

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
        plotter.plot_label_precision(data_set['cannon_data_filtered'],
                                     label_names,
                                     label_reference_values=(data_set['reference_values'],),
                                     colors=(colour,),
                                     legend_labels=("{} ({})".format(data_set['title'], run_title),),
                                     common_x_limits=(0, 250),
                                     common_y_axes=range(2, 18),
                                     pixels_per_angstrom=np.median(1.0 / np.diff(data_set['wavelength_raster'])))

    plotter.fig.savefig(output_figure)


if __name__ == "__main__":

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', required=True, action="append", dest='spectrum_libraries',
                        help="Library of spectra that the Cannon tried to fit.")
    parser.add_argument('--cannon-output', required=True, action="append", dest='cannon_output',
                        help="ASCII table containing the label values estimated by the Cannon.")
    parser.add_argument('--dataset-label', required=True, action="append", dest='data_set_label',
                        help="Title for a set of predictions output from the Cannon, e.g. LRS or HRS.")
    parser.add_argument('--output-file', default="/tmp/cannon_performance_plot.pdf", dest='output_file',
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
                          output_figure=args.output_file,
                          run_title="External" if args.use_reference_labels else "Internal"
                          )
