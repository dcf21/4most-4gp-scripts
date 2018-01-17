#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python2.7 redden_library.py --input-library demo_stars \
                            --output-library demo_stars_reddened \

