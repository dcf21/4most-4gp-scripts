# -*- coding: utf-8 -*-


"""
Define a common command-line interface which is shared between all the scripts for plotting the Cannon's performance.
"""

import os
import sys
import argparse


def fetch_command_line_arguments():
    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cannon-output', action="append", dest='cannon_output',
                        help="Filename of the JSON file containing the label values estimated by the Cannon, without "
                             "the <.summary.json.gz> suffix.")
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

    assert len(args.cannon_output) == len(args.data_set_line_type), \
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
        cannon_filename_full = cannon_output + ".full.json.gz"
        if not os.path.exists(cannon_filename_full):
            print "mean_performance_vs_label.py could not proceed: Cannon run <{}> not found". \
                format(cannon_filename_full)
            sys.exit()

        # Append to list of Cannon data sets
        cannon_outputs.append({'cannon_output': cannon_output,
                               'title': data_set_label,
                               'filters': data_set_filter,
                               'colour': data_set_colour,
                               'line_type': data_set_line_type
                               })

    return {"data_sets": cannon_outputs,
            "abundances_over_h": args.abundances_over_h,
            "assume_scaled_solar": args.assume_scaled_solar,
            "abscissa_label": args.abscissa_label,
            "compare_against_reference_labels": args.use_reference_labels,
            "output_figure_stem": args.output_file,
            "run_title": "",  # "External" if args.use_reference_labels else "Internal"
            }
