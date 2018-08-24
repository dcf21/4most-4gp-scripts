#!../../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python label_tabulator.py>, but <./label_tabulator.py> will not work.

"""

Take an output JSON file produced by the script <test_cannon/cannon_test.py>, which contains the label values estimated
by the Cannon. From this, tabulate the input stellar parameters used to synthesise the spectra, the stellar parameters
estimated by the Cannon, and the formal uncertainty in the Cannon's fitting output. These values are tabulated in an
ASCII data file.

A separate table is produced for each SNR that the Cannon tested.

The list of labels to tabulate should be specified with the "--labels" command line option. If no list is supplied, then
we tabulate all the labels.

The output tables are stored by default in a set of data files in </tmp/cannon_estimates__???.dat> where ??? is an SNR.

This file path can be changed with the --output-stub command line argument.

"""

import os
from os import path as os_path
import numpy as np
import gzip
import argparse
import json


def tabulate_labels(output_stub, labels, cannon, assume_scaled_solar=False):
    # Make sure output directory exists
    os.system("mkdir -p {}".format(os_path.split(output_stub)[0]))

    # library_values[Starname] = [list of label values]
    # cannon_values[Starname][SNR] = [list of label values]
    # cannon_errors[Starname][SNR] = [list of label uncertainties, as estimated by the Cannon]
    library_values = {}
    cannon_values = {}
    cannon_uncertainties = {}

    # Start compiling a list of all the SNR values in the Cannon output
    snr_list = []

    # Load Cannon JSON output
    if not cannon.endswith(".full.json.gz"):
        cannon += ".full.json.gz"
    assert os.path.exists(cannon), "Cannon output file <{}> does not exist.".format(cannon)
    cannon_json = json.loads(gzip.open(cannon).read())

    # If no list of labels supplied, then list everything
    if not labels:
        labels = cannon_json['labels']

    # Open Cannon output data file
    for item in cannon_json["spectra"]:
        # Look up name of object and SNR of spectrum used
        object_name = item["Starname"]
        snr = item["spectrum_metadata"]["SNR"] if "SNR" in item["spectrum_metadata"] else 0

        # Look up Cannon's estimated values of the labels we're interested in
        label_values = []
        for label in labels:
            label_values.append(item["cannon_output"][label])

        # Feed Cannon's estimated values in the cannon_values data structure
        if object_name not in cannon_values:
            cannon_values[object_name] = {}
        cannon_values[object_name][snr] = label_values

        # Keep a list of all the SNRs we've seen
        if snr not in snr_list:
            snr_list.append(snr)

        # Look up the target values for each label
        label_values = []
        for label in labels:
            if label in item["spectrum_metadata"]:
                label_values.append(item["spectrum_metadata"][label])
            elif assume_scaled_solar and ("[Fe/H]" in item["spectrum_metadata"]):
                # If no target value available, scale with [Fe/H]
                label_values.append(item["spectrum_metadata"]["[Fe/H]"])
            else:
                # If even [Fe/H] isn't available, leave blank
                label_values.append(np.nan)

        library_values[object_name] = label_values

        # Look up the Cannon's error estimates for each label
        label_values = []
        for label in labels:
            key = "E_{}".format(label)
            if key in item["cannon_output"]:
                label_values.append(item["cannon_output"][key])
            else:
                label_values.append(np.nan)
        if object_name not in cannon_uncertainties:
            cannon_uncertainties[object_name] = {}
        cannon_uncertainties[object_name][snr] = label_values

    # Start creating output data files
    snr_list_with_filenames = []
    snr_list.sort()
    object_names = library_values.keys()
    object_names.sort()
    for snr in snr_list:
        filename = "{}_{:03.0f}.dat".format(output_stub, snr)
        snr_list_with_filenames.append({
            "snr": snr,
            "filename": filename
        })

        with open(filename, "w") as output:
            # Write headings at the top of the file
            words = []
            for item in labels:
                words.append("in_{}".format(item))
                words.append("out_{}".format(item))
                words.append("err_{}".format(item))
            words.append("Starname")
            output.write("# {}\n".format(" ".join(["{:10s}".format(i) for i in words])))

            # Loop over stars writing them into data file
            for object_name in object_names:
                words = []
                for index, item in enumerate(labels):
                    # Start line with the library parameter values
                    words.append("{:10.4f}".format(library_values[object_name][index]))

                    # Add values which the Cannon estimated at this SNR
                    if (object_name in cannon_values) and (snr in cannon_values[object_name]):
                        words.append("{:10.4f}".format(cannon_values[object_name][snr][index]))
                    else:
                        words.append("{:10s}")

                    # Add uncertainties which the Cannon reported at this SNR
                    if (object_name in cannon_values) and (snr in cannon_values[object_name]):
                        words.append("{:10.4f}".format(cannon_uncertainties[object_name][snr][index]))
                    else:
                        words.append("{:10s}")

                # Add name of object
                words.append(object_name)

                # Write output line
                line = " ".join(words)
                output.write("{}\n".format(line))
    return snr_list_with_filenames


# If we're invoked as a script, read input parameters from the command line
if __name__ == "__main__":
    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', action="append", dest='labels',
                        help="Labels we should output values for.")
    parser.add_argument('--cannon-output',
                        required=True,
                        default="",
                        dest='cannon',
                        help="The Cannon output file we are to tabulate, without file extension. For example, to plot "
                             "<cannon_pepsi_hrs.full.json.gz>, pass the argument <cannon_pepsi_hrs>.")
    parser.add_argument('--assume-scaled-solar',
                        action='store_true',
                        dest="assume_scaled_solar",
                        help="Assume scaled solar abundances for any elements which don't have abundances individually "
                             "specified. There will be no indication in the output table where scaled solar values "
                             "have been inserted; we simply copy the value of [Fe/H].")
    parser.add_argument('--no-assume-scaled-solar',
                        action='store_false',
                        dest="assume_scaled_solar",
                        help="Do not assume scaled solar abundances; the output table will show a dash whenever there "
                             "is missing data.")
    parser.set_defaults(assume_scaled_solar=False)
    parser.add_argument('--output-stub', default="/tmp/cannon_estimates_", dest='output_stub',
                        help="Data file to write output to.")
    args = parser.parse_args()

    tabulate_labels(args.output_stub, args.labels, args.cannon, args.assume_scaled_solar)
