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

# ----------------------

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs_50only[5000<Teff<6000]" \
                       --description "4MOST HRS - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_3label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs_50only[5000<Teff<6000]" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_3label"

python3 cannon_test.py --test "galah_test_sample_4fs_hrs_50only[5000<Teff<6000]" \
                       --reload-cannon "../../../output_data/cannon/cannon_galah_hrs_3label" \
                       --description "4MOST HRS - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_3label_reloaded"

python3 cannon_test.py --test "galah_test_sample_4fs_hrs_50only[5000<Teff<6000]" \
                       --reload-cannon "../../../output_data/cannon/cannon_galah_hrs_3label" \
                       --description "4MOST HRS (censored) - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_3label_reloaded"

# -------------

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs_50only[5000<Teff<6000]" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_10label"

