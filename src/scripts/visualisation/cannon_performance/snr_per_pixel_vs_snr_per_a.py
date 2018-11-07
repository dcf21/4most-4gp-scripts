#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python snr_per_pixel_vs_snr_per_a.py>, but <./snr_per_pixel_vs_snr_per_a.py> will not work.

"""
Calculate the conversion factor between SNR/pixel and SNR/A.
"""

import gzip
import json

import numpy as np
from fourgp_degrade import SNRConverter
from lib.plot_settings import snr_defined_at_wavelength
from offset_cmd_line_interface import fetch_command_line_arguments


def snr_per_pixel_vs_snr_per_a(data_sets, abscissa_label, assume_scaled_solar,
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

    # Loop over the various Cannon runs we have, e.g. LRS and HRS
    for counter, data_set in enumerate(data_sets):

        cannon_output = json.loads(gzip.open(data_set['cannon_output'] + ".full.json.gz", "rt").read())

        # Work out multiplication factor to convert SNR/pixel to SNR/A
        snr_converter = SNRConverter(raster=np.array(cannon_output['wavelength_raster']),
                                     snr_at_wavelength=snr_defined_at_wavelength)

        print("SNR/pixel = 1 corresponds to SNR/A = {}".format(snr_converter.per_pixel(1).per_a()))


if __name__ == "__main__":
    # Read input parameters
    command_line_arguments = fetch_command_line_arguments()
    snr_per_pixel_vs_snr_per_a(**command_line_arguments)
