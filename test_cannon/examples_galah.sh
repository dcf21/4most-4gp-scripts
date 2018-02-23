#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

mkdir -p ../output_data/cannon

# -----------------------------------------------------------------------------------------

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on GALAH 0.25. Test on GALAH 0.75." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_censored_hrs_10label"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 10 labels - Train on GALAH 0.25. Test on GALAH 0.75." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_censored_lrs_10label"

# All stellar labels set of GES stars
# logg, [Nd/H], [O/H], [Mg/H], [V/H], [Ba/H], [Al/H], [Ca/H], [Mn/H], [S/H], [Sc/H], [Ce/H], [Ti/H], [Na/H], [Si/H], [La/H], [Ni/H], [C/H], [Zn/H], [Fe/H], [Co/H], [Cr/H], Teff
