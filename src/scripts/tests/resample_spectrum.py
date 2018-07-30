#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python import_pepsi.py>, but <./import_pepsi.py> will not work.

"""
Create a demo spectrum with a couple of lines in it, and check they look sensible when we resample them.
"""

from math import pi
import numpy as np

from fourgp_speclib import Spectrum
from fourgp_degrade import SpectrumResampler

# Create a really bonkers raster to sample a spectrum on
raster_original = np.concatenate([np.linspace(0, 3, 30), np.linspace(3, 6, 300), np.linspace(6, 10, 20)])


# An analytic function for a spectral line
def lorentzian(x, x0, fwhm):
    return 1 / pi * (0.5 * fwhm) / (np.square(x - x0) + np.square(0.5 * fwhm))


# Create a dummy spectrum
x_in = raster_original
absorption = (lorentzian(x_in, 3, 0.5) +
              lorentzian(x_in, 4.5, 0.2) +
              lorentzian(x_in, 6, 0.01) +
              lorentzian(x_in, 8, 0.2) +
              lorentzian(x_in, 9, 0.01))
spectrum_original = np.exp(-absorption)
spectrum_original_object = Spectrum(wavelengths=raster_original,
                                    values=spectrum_original,
                                    value_errors=np.zeros_like(spectrum_original)
                                    )

# Create list of the spectra we're going to save to disk
output = [spectrum_original_object]

# Create a more sensible raster to sample the spectrum onto
resampler = SpectrumResampler(input_spectrum=spectrum_original_object)
for raster_new in [np.linspace(0, 12, 240), np.linspace(0, 12, 48), np.linspace(0, 12, 24)]:
    spectrum_new_object = resampler.onto_raster(output_raster=raster_new)
    output.append(spectrum_new_object)

for counter, item in enumerate(output):
    item.to_file(filename="/tmp/resampling_demo_{:d}.dat".format(counter),
                 binary=False, overwrite=False)
