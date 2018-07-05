#!../../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python reddening_figure.py>, but <./reddening_figure.py> will not work.

"""
Create a demo showing the solar spectrum being reddened.
"""

import os
from os import path as os_path
import numpy as np
import logging

from base_synthesizer import Synthesizer
from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_degrade import SpectrumReddener
from fourgp_fourfs import FourFS

# Settings
photometric_band = "SDSS_g"
reference_magnitude = 15
ebv_list = [0, 0.5, 1]

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="2018jun_report",
                          root_path="../../..",
                          spectral_resolution=250,
                          logger=logger,
                          docstring=__doc__)

star_list = [
    {'name': "Sun", 'Teff': 5771.8, 'logg': 4.44, '[Fe/H]': 0, 'extra_metadata': {'set_id': 1}},
]

# Pass list of stars to synthesizer
synthesizer.set_star_list(star_list)

# Create new SpectrumLibrary
synthesizer.create_spectrum_library()

# Iterate over the spectra we're supposed to be synthesizing
synthesizer.do_synthesis()

# Close TurboSpectrum synthesizer instance
synthesizer.clean_up()

# Load spectrum
spectra = SpectrumLibrarySqlite.open_and_search(library_spec=synthesizer.args.library,
                                                workspace=synthesizer.workspace,
                                                extra_constraints={"Starname": "Sun", "continuum_normalised": 0}
                                                )
input_library, input_spectra_ids, input_spectra_constraints = [spectra[i] for i in ("library", "items", "constraints")]

input_spectrum_array = input_library.open(ids=input_spectra_ids[0]['specId'])
input_spectrum = input_spectrum_array.extract_item(0)

# Process spectra through reddening model
reddener = SpectrumReddener(input_spectrum=input_spectrum)

# Instantiate 4FS wrapper
etc_wrapper = FourFS(
    path_to_4fs=os_path.join(synthesizer.args.binary_path, "OpSys/ETC"),
    magnitude=reference_magnitude,
    photometric_band=photometric_band,
    snr_list=[50],
    snr_per_pixel=True
)

# Fig 1: Reddened spectra, with flux on vertical axis
reddened_spectrum_data = [input_spectrum.wavelengths]
mag = input_spectrum.photometry(photometric_band)
input_spectrum.values *= pow(10, -0.4 * (reference_magnitude - mag))
for ebv in ebv_list:
    spectrum_reddened = reddener.redden(e_bv=ebv)
    reddened_spectrum_data.append(spectrum_reddened.values)
np.savetxt("/tmp/fig1.dat", np.transpose(reddened_spectrum_data))

# Fig 2: Reddened spectra, holding observed magnitude constant
reddened_spectrum_data = [input_spectrum.wavelengths]
for ebv in ebv_list:
    spectrum_reddened = reddener.redden(e_bv=ebv)
    mag = spectrum_reddened.photometry(photometric_band)
    reddened_spectrum_data.append(spectrum_reddened.values * pow(10, -0.4 * (reference_magnitude - mag)))
np.savetxt("/tmp/fig2.dat", np.transpose(reddened_spectrum_data))

# Fig 3: SNR per pixel across the spectrum
reddened_spectrum_data = [None]
for ebv in ebv_list:
    spectrum_reddened = reddener.redden(e_bv=ebv)
    degraded_spectra = etc_wrapper.process_spectra(spectra_list=((spectrum_reddened, None),))
    mode = "LRS"
    for index in degraded_spectra[mode]:
        for snr in degraded_spectra[mode][index]:
            spectrum_type = "spectrum"
            degraded_spectrum = degraded_spectra[mode][index][snr][spectrum_type]
            reddened_spectrum_data.append(degraded_spectrum.values / degraded_spectrum.value_errors)
            reddened_spectrum_data[0] = degraded_spectrum.wavelengths
np.savetxt("/tmp/fig3.dat", np.transpose(reddened_spectrum_data))

# Clean up 4FS
etc_wrapper.close()

"""

set term png dpi 400
set width 14
set key bottom right
set xrange [3600:9600]
set log y
set xlabel 'Wavelength [\AA]'
set ylabel 'Flux [$\mathrm{erg}/\mathrm{s}/\mathrm{cm}^2/\mathrm{\AA}$]'

set output 'fig1.png'
plot 'fig1.dat' u 1:2 w l col blue title 'E(B-V)\,$=0$', \
     '' u 1:3 w l col orange title 'E(B-V)\,$=0.5$', \
     '' u 1:4 w l col red title 'E(B-V)\,$=1$'

set output 'fig2.png'
plot 'fig2.dat' u 1:2 w l col blue title 'E(B-V)\,$=0$', \
      '' u 1:3 w l col orange title 'E(B-V)\,$=0.5$', \
      '' u 1:4 w l col red title 'E(B-V)\,$=1$'

set output 'fig3.png'
set ylabel 'SNR/pixel'
set nolog y
plot 'fig3.dat' u 1:2 w l col blue title 'E(B-V)\,$=0$', \
      '' u 1:3 w l col orange title 'E(B-V)\,$=0.5$', \
      '' u 1:4 w l col red title 'E(B-V)\,$=1$'

"""
