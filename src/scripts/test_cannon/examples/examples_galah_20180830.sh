#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
mkdir -p ../../../output_data/cannon

# -----------------------------------------------------------------------------------------

for mode in hrs lrs
do

for he_width in 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.1 2.2
do


python2.7 cannon_test.py --train "galah_training_sample_4fs_he1.7_${mode}" \
                         --test "galah_test_sample_4fs_he${he_width}_${mode}" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (with ${he_width}-pixel half-ellipse convolution; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../../../output_data/cannon/cannon_galah_he${he_width}_censored_${mode}_10label"

done

done

