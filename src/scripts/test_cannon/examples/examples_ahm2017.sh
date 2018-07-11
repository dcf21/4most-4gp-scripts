#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../virtualenv/bin/activate

# Now do some work
mkdir -p ../output_data/cannon

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --continuum-normalisation "running_mean" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_cn_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --continuum-normalisation "running_mean" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_cn_10label"

# ----------------------

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --description "4MOST HRS - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_hrs_3label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --description "4MOST LRS - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_lrs_3label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_3label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_3label"

# -----------------------------------------------------------------------------------------

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --description "4MOST HRS - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --description "4MOST LRS - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_lrs_10label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_10label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --censor-scheme 2 \
                         --description "4MOST HRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored2_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --censor-scheme 2 \
                         --description "4MOST LRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored2_lrs_10label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --censor-scheme 3 \
                         --description "4MOST HRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored3_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --censor-scheme 3 \
                         --description "4MOST LRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored3_lrs_10label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250,-1<[Fe/H]<1]" \
                         --test "4fs_ahm2017_perturbed_hrs[-1<[Fe/H]<1]" \
                         --description "4MOST HRS - 10 labels (metallicity cut) - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_fehcut_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250,-1<[Fe/H]<1]" \
                         --test "4fs_ahm2017_perturbed_lrs[-1<[Fe/H]<1]" \
                         --description "4MOST LRS - 10 labels (metallicity cut) - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_fehcut_lrs_10label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250,-5<[Fe/H]<-1]" \
                         --test "4fs_ahm2017_perturbed_hrs[-5<[Fe/H]<-1]" \
                         --description "4MOST HRS - 10 labels (metallicity cut2) - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_fehcut2_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250,-5<[Fe/H]<-1]" \
                         --test "4fs_ahm2017_perturbed_lrs[-5<[Fe/H]<-1]" \
                         --description "4MOST LRS - 10 labels (metallicity cut2) - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_fehcut2_lrs_10label"

# -----------------------------------------------------------------------------------------

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS - 12 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Mg/H],[Ti/H],[Na/H],[Ni/H],[Cr/H],[C/H],[O/H],[Li/H],[Ba/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_12label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS - 12 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Mg/H],[Ti/H],[Na/H],[Ni/H],[Cr/H],[C/H],[O/H],[Li/H],[Ba/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_12label"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS - 10 labels with C, O - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Mg/H],[Ti/H],[Na/H],[Ni/H],[Cr/H],[C/H],[O/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_10label_CO"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS - 10 labels with C, O - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Mg/H],[Ti/H],[Na/H],[Ni/H],[Cr/H],[C/H],[O/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_10label_CO"

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS - 10 labels qith Li, Ba - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Mg/H],[Ti/H],[Na/H],[Ni/H],[Cr/H],[Li/H],[Ba/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_10label_LiBa"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS - 10 labels qith Li, Ba - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Mg/H],[Ti/H],[Na/H],[Ni/H],[Cr/H],[Li/H],[Ba/H]" \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_10label_LiBa"

# -----------------------------------------------------------------------------------------

python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                         --test "4fs_reddened_ahm2017_perturbed_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (reddened; censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_hrs_10label"
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                         --test "4fs_reddened_ahm2017_perturbed_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (reddened; censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_lrs_10label"

# All stellar labels set of GES stars
# logg, [Nd/H], [O/H], [Mg/H], [V/H], [Ba/H], [Al/H], [Ca/H], [Mn/H], [S/H], [Sc/H], [Ce/H], [Ti/H], [Na/H], [Si/H], [La/H], [Ni/H], [C/H], [Zn/H], [Fe/H], [Co/H], [Cr/H], Teff
