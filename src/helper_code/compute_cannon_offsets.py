# -*- coding: utf-8 -*-

"""
A class for calculating the offset in the Cannon's determination of labels from their true values.
"""

import re
import numpy as np

from label_information import LabelInformation
from interpolate_linear import sort_on_first_item


class CannonAccuracyCalculator:
    """
    A class for calculating the offset in the Cannon's determination of labels from their true values.
    """

    def __init__(self, cannon_json_output,
                 label_names,
                 compare_against_reference_labels=True,
                 assume_scaled_solar=False,
                 abscissa_field="SNR"
                 ):
        """
        Initiate a class instance for calculating the offset in the Cannon's determination of labels from their true
        values.

        :param cannon_json_output:
             The JSON data structure which was saved by <cannon_test.py>
        :type cannon_json_output:
            dict
        :param label_names:
            A list of the names of the labels we are computing the Cannon's accuracy for.
        :type label_names:
            list
        :param abscissa_field:
            The name of the field that we are plotting the Cannon's performance against; e.g. "SNR" or "e_bv".
        :type abscissa_field:
            str
        :param compare_against_reference_labels:
            Boolean flag.

            If true, we compare against the stellar parameters and abundances which were used to
            synthesise the test spectra, as recorded in the <target_{}> metadata fields for each star. Where these
            fields are missing, a particular abundance was unknown for this object, and a scaled-solar abundance will
            have been assumed. We may or may not include the object, depending on the <assume_scaled_solar> flag.

            If false, we compare against the stellar parameters and abundances which were derived at the highest SNR
            value available.
        :type compare_against_reference_labels:
            bool
        :param assume_scaled_solar:
            Boolean flag.

            If true, where the abundances of stars are unknown, we test that the Cannon correctly infers
            the scaled-solar abundances which will have been assumed when synthesising the spectra of these objects.

            If false, where the abundances of stars are unknown, we do not include the Cannon's test results (for that
            element in that particular star) in any statistics about its accuracy.
        :type assume_scaled_solar:
            bool

        """

        self.cannon_json_output = cannon_json_output
        self.label_names = label_names
        self.compare_against_reference_labels = compare_against_reference_labels
        self.assume_scaled_solar = assume_scaled_solar
        self.abscissa_field = abscissa_field

        self.label_metadata = LabelInformation().label_metadata

        # Fetch Cannon output
        self.test_items = cannon_json_output['stars']

        # Sort Cannon runs by star name
        self.test_items_by_star_name = {}
        for index, tests_for_this_star in enumerate(self.test_items):
            star_name = self.test_items[index]['Starname']
            abscissa_value = tests_for_this_star[abscissa_field]

            # If we have not seen this star before, create an entry for it in test_items_by_star_name
            if star_name not in self.test_items_by_star_name:
                self.test_items_by_star_name[star_name] = []

            self.test_items_by_star_name[star_name].append([abscissa_value, index])

        # We now create a look-up table of the target / reference values for each label for each star
        self.reference_values = {}
        self.label_offsets = None

        # Loop over all the stars in the test set
        for star_name in self.test_items_by_star_name:

            # Sort Cannon runs into order of ascending abscissa value
            self.test_items_by_star_name[star_name].sort(sort_on_first_item)
            test_at_highest_abscissa = self.test_items[self.test_items_by_star_name[star_name][-1][1]]

            # Start building a tree of the reference values by star name, and then by label name
            reference_values = {}

            # Loop over all of the labels we're computing the Cannon's accuracy for
            for label in label_names:
                label_info = self.label_metadata[label]
                cannon_label = label_info["cannon_label"]

                # Look up the target value for this label, which we're comparing the Cannon against

                # Option 1: Compare the Cannon's output against the values that were used to synthesise this spectrum
                if compare_against_reference_labels:
                    target_metadata_field = "target_{}".format(cannon_label)

                    # If this star has a field called target_[X/H], we use the value of this as the target for [X/H]
                    if target_metadata_field in test_at_highest_abscissa:
                        reference_values[label] = test_at_highest_abscissa[target_metadata_field]

                    # If not, then this abundance is unknown for this star. Is we're allowed to assume scaled solar
                    # abundances, we look up the value of target_[Fe/H] instead
                    elif assume_scaled_solar and ("target_[Fe/H]" in test_at_highest_abscissa):
                        reference_values[label] = test_at_highest_abscissa["target_[Fe/H]"]

                    # If we still don't have a target value, then set it to NaN
                    else:
                        reference_values[label] = np.nan

                    # If we are plotting abundance over Fe, then [X/Fe] = [X/H] / [Fe/H]
                    if label_info["over_fe"]:
                        reference_values[label] -= test_at_highest_abscissa["target_[Fe/H]"]

                # Option 2: Compare the Cannon's output against the estimates it produces at the highest abscissa value
                else:
                    reference_values[label] = test_at_highest_abscissa[cannon_label]

                    # If we are plotting abundance over Fe, then [X/Fe] = [X/H] / [Fe/H]
                    if label_info["over_fe"]:
                        reference_values[label] -= test_at_highest_abscissa["[Fe/H]"]

            # Dictionary of the target values for each label we're testing, for each named star in the test set
            self.reference_values[star_name] = reference_values

    def calculate_cannon_offsets(self, filter_on_indices=None):
        """
        :param filter_on_indices:
            An optional list of the indices of the test spectra we want to include in our calculation of the Cannon's
            performance. This is used if we want to do cuts, e.g. [Fe/H] using the method <filter_test_stars>, and then
            apply that cut when looking through all the spectra the Cannon tried to fit and calculating the offsets in
            its estimates.
        :type filter_on_indices:
            list
        :return:
            None
        """

        # We create a dictionary of the Cannon's offsets at each abscissa value, and for each label
        self.label_offsets = {}

        # Loop over all the stars in the test set
        for star_name in self.test_items_by_star_name:
            reference_values = self.reference_values[star_name]

            # Loop over all of the labels we're computing the Cannon's accuracy for
            for label in self.label_names:
                label_info = self.label_metadata[label]
                cannon_label = label_info["cannon_label"]

                # Now see how far the Cannon was away from this target value
                # Loop over all the abscissa values we tested this star at
                for abscissa_value, test_item_index in self.test_items_by_star_name[star_name]:

                    # Skip this spectrum if it is excluded from the test sample by some constraint
                    if (filter_on_indices is not None) and (test_item_index not in filter_on_indices):
                        continue

                    test_item = self.test_items[test_item_index]

                    # Look up the Cannon's estimate for this label
                    cannon_estimate = np.nan
                    if label in test_item:
                        cannon_estimate = test_item[cannon_label]

                    # If we are testing [X/Fe] rather than [X/H], then do conversion using the Cannon's estimate of
                    # [Fe/H]
                    if label_info["over_fe"]:
                        cannon_estimate -= test_item["[Fe/H]"]

                    cannon_offset = cannon_estimate - reference_values[label]

                    # Add the offset in this label estimate to the statistics in <self.label_offsets>

                    # If we've not seen this abscissa value before, we need to create a dictionary for it
                    if abscissa_value not in self.label_offsets:
                        self.label_offsets[abscissa_value] = {}

                    # If we've not seen this label for it, start a list of the offsets for this label
                    if label not in self.label_offsets[abscissa_value]:
                        self.label_offsets[abscissa_value][label] = []

                    # File this offset, even if it is NaN. This is vital as some codes require that we return a
                    # consistent number of offsets for every label (for example, when making histograms, we record
                    # the offsets for each star in a giant table, with one row per star).
                    self.label_offsets[abscissa_value][label].append(cannon_offset)

    def filter_test_stars(self, constraints):
        """
        Select only those stars from the test set which meet certain constraints, these are specified as strings, e.g.
        "[Fe/H]<0"

        :param constraints:
            A list of string constraints on label values
        :type constraints:
            list
        :return:
            A list of the indexes within the list of test stars of those which meet the supplied constraints
        """

        # A list of Cannon output for stars which meet the filter criteria
        output_index_list = []

        # Loop over each test item in turn to see if it meets the supplied constraints
        for index, test_item in enumerate(self.test_items):
            star_name = test_item['Starname']
            reference_values = self.reference_values[star_name]

            meets_all_filters = True

            # Test this star against each test object in turn
            for constraint in constraints:

                # Ignore blank constraints
                constraint = constraint.strip()
                if constraint == "":
                    continue

                # Split the constraint into a label name, and a label value, with an operator in the middle
                constraint_label = re.split("[<=>]", constraint)[0]
                constraint_value_string = re.split("[<=>]", constraint)[-1]
                constraint_value = constraint_value_string
                try:
                    constraint_value = float(constraint_value)
                except ValueError:
                    pass

                # If this is one of the labels the Cannon is fitting, we apply cut on the *target* value of this label,
                # not the one output by the Cannon
                if constraint_label in reference_values:
                    reference_value = reference_values[constraint_label]

                # Alternatively, we can also apply cuts on parameters like SNR and e_bv, which are unique to each
                # spectrum, rather than to each star
                else:
                    reference_value = test_item[constraint_label]

                # Test whether this spectrum meets this filter
                if constraint == "{}={}".format(constraint_label, constraint_value_string):
                    meets_filter = (reference_value == constraint_value)

                elif constraint == "{}<={}".format(constraint_label, constraint_value_string):
                    meets_filter = (reference_value <= constraint_value)

                elif constraint == "{}<{}".format(constraint_label, constraint_value_string):
                    meets_filter = (reference_value < constraint_value)

                elif constraint == "{}>={}".format(constraint_label, constraint_value_string):
                    meets_filter = (reference_value >= constraint_value)

                elif constraint == "{}>{}".format(constraint_label, constraint_value_string):
                    meets_filter = (reference_value > constraint_value)

                else:
                    assert False, "Could not parse constraint <{}>.".format(constraint)

                if not meets_filter:
                    meets_all_filters = False
                    break

            # If this spectrum has met all the supplied filters, then we include it in the output set
            if meets_all_filters:
                output_index_list.append(index)

        # Return output set
        return output_index_list
