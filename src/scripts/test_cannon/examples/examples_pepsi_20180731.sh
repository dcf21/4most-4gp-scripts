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
                         --test "pepsi_4fs_hrs" \
                         --description "4MOST HRS - 5 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../../../output_data/cannon/cannon_pepsi_hrs_5label"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "pepsi_4fs_lrs" \
                         --description "4MOST LRS - 5 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../../../output_data/cannon/cannon_pepsi_lrs_5label"

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "pepsi_4fs_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 5 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../../../output_data/cannon/cannon_pepsi_censored_hrs_5label"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "pepsi_4fs_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 5 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../../../output_data/cannon/cannon_pepsi_censored_lrs_5label"

# -----------------------------------------------------------------------------------------


