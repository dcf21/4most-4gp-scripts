#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
python3 list_exposure_times_from_fits.py --input "/media/dcf21/LOUISEUSB/templates_S4_*/*.fits"

