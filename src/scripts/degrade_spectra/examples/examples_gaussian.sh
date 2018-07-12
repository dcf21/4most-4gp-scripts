#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
python2.7 degrade_library_with_gaussian.py --input-library demo_stars \
                                           --output-library-lrs gaussian_demo_stars_lrs \
                                           --output-library-hrs gaussian_demo_stars_hrs
