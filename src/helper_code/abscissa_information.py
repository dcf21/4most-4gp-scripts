# -*- coding: utf-8 -*-

"""
Metadata data about all of the horizontal axes that we can plot precision against. When invoking any of the
<offset_*.py> scripts, the argument "abscissa_label" should be one of the keys to this dictionary.
"""


class AbscissaInformation:
    """
    Metadata data about all of the horizontal axes that we can plot precision against. When invoking any of the
    <offset_*.py> scripts, the argument "abscissa_label" should be one of the keys to this dictionary.
    """

    def __init__(self):
        self.abscissa_labels = {
            # label name, latex label, log axes, axis range
            "SNR/A": {
                "field": "SNR",
                "latex": "$S/N$ $[{\\rm \\AA}^{-1}]$",
                "log_axis": False,
                "box_whisker_width": 1.2,
                "axis_range": (0, 250)},
            "SNR/pixel": {
                "field": "SNR",
                "latex": "$S/N$ $[{\\rm pixel}^{-1}]$",
                "log_axis": False,
                "box_whisker_width": 1.2,
                "axis_range": (0, 250)},
            "ebv": {
                "field": "e_bv",
                "latex": "$E(B-V)$",
                "log_axis": True,
                "box_whisker_width": 1.024,
                "axis_range": (0.04, 3)},
            "rv": {
                "field": "rv",
                "latex": "RV [m/s]",
                "log_axis": True,
                "box_whisker_width": 1.024,
                "axis_range": (800, 50e3)},
            "convolution": {
                "field": "convolution_width",
                "latex": "Convolution Width / pixel",
                "log_axis": False,
                "box_whisker_width": 0.01,
                "axis_range": (1.19, 2.21)},
        }
