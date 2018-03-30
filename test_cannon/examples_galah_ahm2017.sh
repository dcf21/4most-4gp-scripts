#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

mkdir -p ../output_data/cannon

python2.7 cannon_test.py --train "4fs_ahm2017_sample_250only_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_hrs" \
                         --continuum-normalisation "running_mean" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on AHM2017. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_ahm2017_censored_hrs_cn_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_250only_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_lrs" \
                         --continuum-normalisation "running_mean" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 10 labels - Train on AHM2017. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_ahm2017_censored_lrs_cn_10label"

# -----------------------------------------------------------------------------------------

python2.7 cannon_test.py --train "4fs_ahm2017_sample_250only_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_hrs" \
                         --description "4MOST HRS - 10 labels - Train on AHM2017. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_ahm2017_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_250only_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_lrs" \
                         --description "4MOST LRS - 10 labels - Train on AHM2017. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_ahm2017_lrs_10label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_250only_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on AHM2017. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_ahm2017_censored_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_250only_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 10 labels - Train on AHM2017. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_ahm2017_censored_lrs_10label"


