#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python2.7 list_spectra.py --library "turbospec_demo_stars"
python2.7 list_spectra.py --library "turbospec_demo_stars[5100<Teff<0]"

python2.7 export_spectra.py --library "turbospec_demo_stars[Starname=Sun]"

python2.7 spectrum_library_to_csv.py --library "turbospec_demo_stars"

