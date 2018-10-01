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
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_00"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_00"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_00"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_00"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Mg/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_01"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Mg/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_01"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Mg/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_01"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Mg/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_01"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ti/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_02"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ti/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_02"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ti/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_02"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ti/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_02"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Si/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_03"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Si/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_03"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Si/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_03"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Si/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_03"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Na/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_04"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Na/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_04"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Na/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_04"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Na/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_04"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ni/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_05"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ni/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_05"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ni/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_05"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ni/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_05"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Cr/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_06"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Cr/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_06"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Cr/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_06"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Cr/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_06"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ba/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_07"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ba/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_07"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ba/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_07"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ba/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_07"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Eu/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_08"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Eu/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_08"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Eu/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_08"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Eu/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_08"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Li/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_09"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Li/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_09"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Li/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_09"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Li/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_09"

# -----------------------------------------------------------------------------------------


python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[C/H],[O/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_individual_10"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[C/H],[O/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_individual_10"

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[C/H],[O/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_hrs_individual_10"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[C/H],[O/H]" \
                       --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                       --output-file "../../../output_data/cannon/cannon_galah_censored_lrs_individual_10"

# -----------------------------------------------------------------------------------------




