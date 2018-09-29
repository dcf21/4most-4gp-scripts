#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python label_tabulator.py>, but <./label_tabulator.py> will not work.

"""
Take a SpectrumLibrary and tabulate a list of the stellar parameters of the stars within it.
"""

import argparse
import re
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
        # Loop over each spectrum library in turn
        for library in library_list:

            # Extract name of spectrum library we are to open. Filter off any constraints which follow the name in []
            test = re.match("([^\[]*)\[(.*)\]$", library)
            if test is None:
                library_name = library
            else:
                library_name = test.group(1)

            # Open spectrum library and extract list of metadata fields which are defined on this library
            library_path = os_path.join(workspace, library_name)
            library_object = SpectrumLibrarySqlite(path=library_path, create=False)
            metadata_fields = library_object.list_metadata_fields()

            # Now search library for spectra matching any input constraints, with additional constraint on only
            # returning continuum normalised spectra, if that field is defined for this library
            constraints = {}
            if "continuum_normalised" in metadata_fields:
                constraints["continuum_normalised"] = 1

            library_spectra = SpectrumLibrarySqlite.open_and_search(
                library_spec=library,
                workspace=workspace,
                extra_constraints=constraints
            )

            # Write column headers at the top of the output
            columns = label_list if label_list is not None else library_object.list_metadata_fields()
            output.write("# ")
            for label in columns:
                output.write("{} ".format(label))
            output.write("\n")

            # Loop over objects in each spectrum library
            for item in library_spectra["items"]:
                metadata = library_object.get_metadata(ids=item['specId'])[0]

                for label in columns:
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
