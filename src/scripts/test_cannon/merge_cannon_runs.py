#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python merge_cannon_runs.py>, but <./concatenate_cannon_runs.py> will not work.

"""

Take multiple output JSON files produced by the script <test_cannon/cannon_test.py>, which contains the label values
estimated by the Cannon. Merge these into a single JSON output file containing all of the label values determined by
all of the Cannon runs.

This makes sense if you are going multiple 5+1 fits to find different elements individually, and then want to plot
all of the elements together.

"""

import argparse
import gzip
import json
import logging


def merge_data_sets(logger, input_files, output_file):
    """
    Merge the JSON files produced by multiple runs of the Cannon into one combined file.

    :param logger:
        A logging object
    :param input_files:
        Filename of an input JSON file containing the label values estimated by the Cannon,
        without the <.summary.json.gz> suffix.
    :param output_file:
        Filename of the output JSON file we are to produce, containing the merged label
        values estimated by the Cannon, without the <.summary.json.gz> suffix.
    :return:
        None
    """

    # Define the format that we use when renaming labels which appear in multiple Cannon runs
    label_renaming_format = "{name}_{number:03d}"

    output_struct = {}

    # Pass 1: Compile a list of all the labels fitted in all of the Cannon runs we're merging
    cannon_summaries = []
    label_names_seen = []
    labels_to_rename = []
    for counter, input_file in enumerate(input_files):
        # Print status update
        logger.info("Pass 1: reading list of labels in <{}>...".format(input_file))

        # Read JSON output
        cannon_summaries.append(json.loads(gzip.open(input_file + ".summary.json.gz", "rt").read()))

        # If this is the first Cannon run, we pass its metadata into the output JSON file
        if counter == 0:
            output_struct = dict(cannon_summaries[-1])  # Copy dictionary, preserving original

        # Loop over all the label names in this Cannon run, and test if we've seen then in previous runs.
        for label_name in cannon_summaries[-1]['labels']:
            if label_name in label_names_seen:
                # If yes, we'll need to rename these labels when we merge
                if label_name not in labels_to_rename:
                    labels_to_rename.append(label_name)
            else:
                # If not, add label name to list of labels we've seen
                label_names_seen.append(label_name)

    # Report status
    if len(labels_to_rename) > 0:
        logger.info("The following labels are repeated in multiple Cannon runs: {}".format(sorted(labels_to_rename)))
        logger.info("They will be renamed with a suffix to indicate which values came from which Cannon runs.")

    # Wipe fields in output structure that we're going to rebuild
    output_struct['labels'] = []

    # Pass 2: Begin merging the Cannon runs
    spectra_output_by_uid = {}
    for counter, input_file in enumerate(input_files):
        # Print status update
        logger.info("Pass 2: merging label values from <{}>...".format(input_file))

        # Read JSON output
        cannon_output = json.loads(gzip.open(input_file + ".full.json.gz", "rt").read())

        # Append list of labels from this Cannon run to our output
        for label_name in cannon_output['labels']:
            if label_name in labels_to_rename:
                output_struct['labels'].append(label_renaming_format.format(name=label_name, number=counter))
            else:
                output_struct['labels'].append(label_name)

        # Merge the label values to the complete list
        for spectrum in cannon_output['spectra']:
            uid = spectrum['uid']

            # Rename labels in cannon_output
            for label_name in cannon_output['labels']:
                if label_name in labels_to_rename:
                    label_name_new = label_renaming_format.format(name=label_name, number=counter)
                    spectrum['cannon_output'][label_name_new] = spectrum['cannon_output'][label_name]
                    del spectrum['cannon_output'][label_name]

            # If this is the first time we've seen this spectrum, create a new entry for it in output data file
            if uid not in spectra_output_by_uid:
                spectra_output_by_uid[uid] = spectrum

            # Otherwise, we merge labels from this Cannon run into the existing entry
            else:
                spectra_output_by_uid[uid]['cannon_output'].update(spectrum['cannon_output'])

            # Copy label target values in "spectrum_metadata"
            for label_name in labels_to_rename:
                if label_name in spectra_output_by_uid[uid]['spectrum_metadata']:
                    label_name_new = label_renaming_format.format(name=label_name, number=counter)
                    spectra_output_by_uid[uid]['spectrum_metadata'][label_name_new] = \
                        spectra_output_by_uid[uid]['spectrum_metadata'][label_name]

        # Free up some memory
        del cannon_output

    # Now set some metadata of our own in the output JSON file
    output_struct['generator'] = __file__
    output_struct['merged_from_files'] = str(input_files)
    output_struct['merged_from_label_lists'] = str([item['labels'] for item in cannon_summaries])

    # Write brief summary of run to JSON file, without masses of data
    logger.info("Writing summary JSON file.")
    with gzip.open("{:s}.summary.json.gz".format(output_file), "wt") as f:
        f.write(json.dumps(output_struct, indent=2))

    # Write full results to JSON file
    logger.info("Creating list of all labels for each spectrum.")
    output_struct["spectra"] = list(spectra_output_by_uid.values())
    del spectra_output_by_uid
    logger.info("Writing full JSON file.")
    with gzip.open("{:s}.full.json.gz".format(output_file), "wt") as f:
        f.write(json.dumps(output_struct, indent=2))
    logger.info("Finished.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-file', action="append", dest='input_files',
                        help="Filename of an input JSON file containing the label values estimated by the Cannon, "
                             "without the <.summary.json.gz> suffix.")
    parser.add_argument('--output-file', required=True, dest='output_file',
                        help="Filename of the output JSON file we are to produce, containing the concatenated label "
                             "values estimated by the Cannon, without the <.summary.json.gz> suffix.")
    args = parser.parse_args()

    # Do the merge
    merge_data_sets(logger=logger,
                    input_files=args.input_files,
                    output_file=args.output_file)
