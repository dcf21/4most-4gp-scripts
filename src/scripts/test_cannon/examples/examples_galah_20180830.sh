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

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_he_hrs_50only" \
                         --description "4MOST HRS (with half-ellipse convolution) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../../../output_data/cannon/cannon_galah_he_hrs_10label"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_he_lrs_50only" \
                         --description "4MOST LRS (with half-ellipse convolution) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../../../output_data/cannon/cannon_galah_he_lrs_10label"

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_he_hrs_50only" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (with half-ellipse convolution; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../../../output_data/cannon/cannon_galah_he_censored_hrs_10label"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_he_lrs_50only" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (with half-ellipse convolution; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../../../output_data/cannon/cannon_galah_he_censored_lrs_10label"


