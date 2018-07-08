# -*- coding: utf-8 -*-

"""
All of the horizontal axes we can plot precision against. The parameter "abscissa_label" should be one of the
keys to this dictionary.
"""


class AbcissaInformation:
    def __init__(self):
        self.abscissa_labels = {
            # label name, latex label, log axes, axis range
            "SNR/A": ["SNR", "$S/N$ $[{\\rm \\AA}^{-1}]$", False, (0, 250)],
            "SNR/pixel": ["SNR", "$S/N$ $[{\\rm pixel}^{-1}]$", False, (0, 250)],
            "ebv": ["e_bv", "$E(B-V)$", True, (0.04, 3)],
            "rv": ["rv", "RV [m/s]", True, (800, 50e3)]
        }
