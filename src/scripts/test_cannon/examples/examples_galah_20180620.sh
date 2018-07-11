#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

mkdir -p ../output_data/cannon

# -----------------------------------------------------------------------------------------


python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_hrs" \
                         --description "4MOST HRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H]" \
                         --labels-individual "[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H],[Ba/H],[Eu/H],[Li/H],[C/H]+[O/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../output_data/cannon/cannon_galah_hrs_individual"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_lrs" \
                         --description "4MOST LRS - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H]" \
                         --labels-individual "[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H],[Ba/H],[Eu/H],[Li/H],[C/H]+[O/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../output_data/cannon/cannon_galah_lrs_individual"

python2.7 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                         --test "galah_test_sample_4fs_hrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H]" \
                         --labels-individual "[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H],[Ba/H],[Eu/H],[Li/H],[C/H]+[O/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../output_data/cannon/cannon_galah_censored_hrs_individual"
python2.7 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                         --test "galah_test_sample_4fs_lrs" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 5+n labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                         --labels "Teff,logg,[Fe/H]" \
                         --labels-individual "[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H],[Ba/H],[Eu/H],[Li/H],[C/H]+[O/H]" \
                         --label-expressions "photometry_GROUND_JOHNSON_B-photometry_GROUND_JOHNSON_V,photometry_GROUND_JOHNSON_V-photometry_GROUND_COUSINS_R" \
                         --output-file "../output_data/cannon/cannon_galah_censored_lrs_individual"

# -----------------------------------------------------------------------------------------


