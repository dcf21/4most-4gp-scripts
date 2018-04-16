#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

mkdir -p ../output_data/cannon

# ----------------------
# S4 test -- produce precision vs SNR plot for s4grn and s4red SNR definitions

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_s4grn_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_s4grn_censored_hrs_10label"

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_s4red_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_s4red_censored_hrs_10label"

# ----------------------
# S4 test -- produce precision vs E(B-V) plots for s4grn and s4red SNR definitions

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_reddened_4fs_snr50_s4grn_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (reddened; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_reddened_censored_snr50_s4grn_hrs_10label"

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_reddened_4fs_snr50_s4red_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (reddened; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_reddened_censored_snr50_s4red_hrs_10label"

# ----------------------
# IWG7 test - produce precision vs E(B-V) plots for our SNR definition

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_reddened_4fs_snr50_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (reddened; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_reddened_censored_snr50_hrs_10label"

python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_reddened_4fs_snr50_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (reddened; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_reddened_censored_snr50_lrs_10label"

# ----------------------
# IWG7 test - produce precision vs E(B-V) plots for our SNR definition, with running mean normalisation

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_reddened_4fs_snr50_hrs" \
                         --continuum-normalisation "running_mean" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (reddened; censored; RMN) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_reddened_censored_snr50_hrs_cn_10label"

python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_reddened_4fs_snr50_lrs" \
                         --continuum-normalisation "running_mean" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (reddened; censored; RMN) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_reddened_censored_snr50_lrs_cn_10label"

# ----------------------
# IWG7 test - produce precision vs RV plot for test spectra with uncorrected radial velocities

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_withrv_4fs_snr50_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (withrv; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_withrv_censored_snr50_hrs_10label"

python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_withrv_4fs_snr50_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (withrv; censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_galah_withrv_censored_snr50_lrs_10label"

# ----------------------
