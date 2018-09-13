#!../../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python concatenate_cannon_runs.py>, but <./concatenate_cannon_runs.py> will not work.

"""

Take multiple output JSON files produced by the script <test_cannon/cannon_test.py>, which contains the label values
estimated by the Cannon. Concatenate these into a single JSON output file containing all of the tests from all of
the files.

This makes sense if multiple Cannon runs have been done at different SNRs, or different values of reddening, and
you wish to plot all the results on a single plot.

It's probably not a good idea to merge Cannon runs with different training sets.

"""

import argparse
import gzip
import json


def concatenate_data_sets(input_files, output_file):
    """
    Concatenate the JSON files produced by multiple runs of the Cannon into one combined file.

    :param input_files:
        Filename of an input JSON file containing the label values estimated by the Cannon,
        without the <.summary.json.gz> suffix.
    :param output_file:
        Filename of the output JSON file we are to produce, containing the concatenated label
        values estimated by the Cannon, without the <.summary.json.gz> suffix.
    :return:
        None
    """

    output_struct = {}
    spectra = []

    for counter, input_file in enumerate(input_files):
        # Print status update
        print "Loading <{}>...".format(input_file)

        # Read JSON output
        cannon_output = json.loads(gzip.open(input_file + ".full.json.gz").read())

        # Append the spectra tested in this Cannon run to the complete list we are making
        spectra.extend(cannon_output['spectra'])

        # If this is the first Cannon run, we pass its metadata into the output JSON file
        if counter == 0:
            del cannon_output['spectra']
            output_struct = cannon_output

    # Now set some metadata of our own in the output JSON file
    output_struct['generator'] = __file__

    # Write brief summary of run to JSON file, without masses of data
    with gzip.open("{:s}.summary.json.gz".format(output_file), "w") as f:
        f.write(json.dumps(output_struct, indent=2))

    # Write full results to JSON file
    output_struct["spectra"] = spectra
    with gzip.open("{:s}.full.json.gz".format(output_file), "w") as f:
        f.write(json.dumps(output_struct, indent=2))


if __name__ == "__main__":
    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-file', action="append", dest='input_files',
                        help="Filename of an input JSON file containing the label values estimated by the Cannon, "
                             "without the <.summary.json.gz> suffix.")
    parser.add_argument('--output-file', required=True, dest='output_file',
                        help="Filename of the output JSON file we are to produce, containing the concatenated label "
                             "values estimated by the Cannon, without the <.summary.json.gz> suffix.")
    args = parser.parse_args()

    # Do the concatenation
    concatenate_data_sets(input_files=args.input_files,
                          output_file=args.output_file)
