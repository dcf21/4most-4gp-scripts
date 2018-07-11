#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../virtualenv/bin/activate

# Now do some work

# The python argparse module doesn't like string values which start with dash characters, which I think is a bug
# So, write " -1<[Fe/H]<0.2" with a space at the beginning to coax it into doing the right thing...

python2.7 filter_cannon_output.py --input-file "../output_data/cannon/cannon_ahm2017_perturbed_hrs_10label" \
                                  --criteria " -1<[Fe/H]<0.2" \
                                  --output-file "../output_data/cannon/filtered_ahm2017_perturbed_hrs_10label"

python2.7 filter_cannon_output.py --input-file "../output_data/cannon/cannon_ahm2017_perturbed_lrs_10label" \
                                  --criteria " -1<[Fe/H]<0.2" \
                                  --output-file "../output_data/cannon/filtered_ahm2017_perturbed_lrs_10label"

