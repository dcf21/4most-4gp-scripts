#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

mkdir -p ../output_data/cannon

# -----------------------------------------------------------------------------------------


python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "pepsi_4fs_hrs" \
                         --description "4MOST HRS - 10 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --output-file "../output_data/cannon/cannon_pepsi_hrs"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "pepsi_4fs_lrs" \
                         --description "4MOST LRS - 10 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --output-file "../output_data/cannon/cannon_pepsi_lrs"

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "pepsi_4fs_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --output-file "../output_data/cannon/cannon_pepsi_censored_hrs"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "pepsi_4fs_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 10 labels - Train on 0.25 GALAH. Test on PEPSI." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --output-file "../output_data/cannon/cannon_pepsi_censored_lrs"

# -----------------------------------------------------------------------------------------


