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

python3 cannon_test.py --train "galah_wm_training_sample_4fs_hrs[SNR=250]" \
                       --test "pepsi_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R_without_cores.txt" \
                       --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on PEPSI." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_pepsi_censored_wm_nocores_hrs"

python3 cannon_test.py --train "galah_wm_training_sample_4fs_lrs[SNR=250]" \
                       --test "pepsi_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R_without_cores.txt" \
                       --description "4MOST LRS (censored) - 10 labels - Train on 0.25 GALAH. Test on PEPSI." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_pepsi_censored_wm_nocores_lrs"

python3 cannon_test.py --train "galah_wm_training_sample_4fs_hrs[SNR=250]" \
                       --test "pepsi_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R_without_cores.txt" \
                       --description "4MOST HRS (censored) - 5 labels - Train on 0.25 GALAH. Test on PEPSI." \
                       --labels "Teff,logg,[Fe/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_pepsi_censored_wm_nocores_hrs_5label"

python3 cannon_test.py --train "galah_wm_training_sample_4fs_lrs[SNR=250]" \
                       --test "pepsi_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R_without_cores.txt" \
                       --description "4MOST LRS (censored) - 5 labels - Train on 0.25 GALAH. Test on PEPSI." \
                       --labels "Teff,logg,[Fe/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_pepsi_censored_wm_nocores_lrs_5label"

# -----------------------------------------------------------------------------------------


