#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
mkdir -p ../../../output_data/payne

# ----------------------

python3 payne_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                      --test "galah_test_sample_4fs_hrs" \
                      --description "4MOST HRS - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../../../output_data/payne/payne_galah_hrs_3label"

