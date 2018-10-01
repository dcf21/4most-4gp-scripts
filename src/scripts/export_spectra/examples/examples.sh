#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
python3 list_spectra.py --library "turbospec_demo_stars"

python3 list_spectra.py --library "turbospec_demo_stars[5100<Teff<0]"

python3 export_spectra.py --library "turbospec_demo_stars[Starname=Sun]"

python3 spectrum_library_to_csv.py --library "turbospec_demo_stars"

