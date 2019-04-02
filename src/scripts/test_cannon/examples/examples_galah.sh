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
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_3label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_3label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_3label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 3 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_3label"

# -----------------------------------------------------------------------------------------

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_10label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_10label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --censor-scheme 2 \
                       --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored2_hrs_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --censor-scheme 2 \
                       --description "4MOST LRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored2_lrs_10label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --censor-scheme 3 \
                       --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored3_hrs_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --censor-scheme 3 \
                       --description "4MOST LRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored3_lrs_10label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250,-1<[Fe/H]<1]" \
                       --test "galah_test_sample_4fs_hrs[-1<[Fe/H]<1]" \
                       --description "4MOST HRS - 10 labels (metallicity cut) - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_fehcut_hrs_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250,-1<[Fe/H]<1]" \
                       --test "galah_test_sample_4fs_lrs[-1<[Fe/H]<1]" \
                       --description "4MOST LRS - 10 labels (metallicity cut) - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_fehcut_lrs_10label"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250,-5<[Fe/H]<-1]" \
                       --test "galah_test_sample_4fs_hrs[-5<[Fe/H]<-1]" \
                       --description "4MOST HRS - 10 labels (metallicity cut2) - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_fehcut2_hrs_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250,-5<[Fe/H]<-1]" \
                       --test "galah_test_sample_4fs_lrs[-5<[Fe/H]<-1]" \
                       --description "4MOST LRS - 10 labels (metallicity cut2) - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_fehcut2_lrs_10label"

# -----------------------------------------------------------------------------------------

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS - 12 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H],[C/H],[Eu/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_12label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS - 12 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H],[C/H],[Eu/H]" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_12label"

# -----------------------------------------------------------------------------------------

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --continuum-normalisation "running_mean" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_cn_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --continuum-normalisation "running_mean" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_cn_10label"

