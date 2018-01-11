#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python2.7 degrade_library_with_gaussian.py --input-library demo_stars \
                                           --output-library-lrs gaussian_demo_stars_lrs \
                                           --output-library-hrs gaussian_demo_stars_hrs
