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

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 12 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_12label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 12 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_12label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 12 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_12label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 12 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_12label"

# -----------------------------------------------------------------------------------------


