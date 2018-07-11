#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python label_tabulator.py>, but <./label_tabulator.py> will not work.

"""
Take a SpectrumLibrary and tabulate a list of the stellar parameters of the stars within it.
"""

import argparse
from os import path as os_path

from fourgp_speclib import SpectrumLibrarySqlite


def tabulate_labels(library_list, label_list, output_file, workspace=None):
    """
    Take a SpectrumLibrary and tabulate a list of the stellar parameters of the stars within it.

    :param workspace:
        Path to the workspace where we expect to find SpectrumLibraries stored
    :param library_list:
        A list of the SpectrumLibraries we are to tabulate the contents of
    :param label_list:
        A list of the labels whose values we are to tabulate
    :param output_file:
        The filename of the ASCII output file we are to produce
    :return:
        None
    """

    # Set path to workspace where we expect to find libraries of spectra
    if workspace is None:
        our_path = os_path.split(os_path.abspath(__file__))[0]
        workspace = os_path.join(our_path, "../../../../workspace")

    # Open output data file
    with open(output_file, "w") as output:
        # Open spectrum libraries in turn
        for library in library_list:
            library_path = os_path.join(workspace, library)
            library_object = SpectrumLibrarySqlite(path=library_path, create=False)

            # Loop over objects in each spectrum library
            # If we're running on 4FS output, we might want to insert a constraint on SNR here as well, but assume we
            # usually run on Turbospectrum output with only one spectrum per star
            constraints = {"continuum_normalised": 1}

            for item in library_object.search(**constraints):
                metadata = library_object.get_metadata(ids=item['specId'])[0]

                for label in (label_list if label_list is not None else library_object.list_metadata_fields()):
                    output.write("{} ".format(metadata.get(label, "-")))
                output.write("\n")


# If we're invoked as a script, read input parameters from the command line
if __name__ == "__main__":
    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', required=True, action="append", dest='libraries',
                        help="Library of spectra we should output stellar labels for.")
    parser.add_argument('--label', action="append", dest='labels',
                        help="Labels we should output values for.")
    parser.add_argument('--output-file', default="/tmp/label_values.dat", dest='output_file',
                        help="Data file to write output to.")
    args = parser.parse_args()

    tabulate_labels(library_list=args.libraries,
                    label_list=args.labels,
                    output_file=args.output_file)
