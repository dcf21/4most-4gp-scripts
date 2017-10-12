#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

mkdir -p ../output_data/cannon

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250,4800<Teff<9999]" \
                      --test "4fs_apokasc_test_set_lrs[4900<Teff<9999]" \
                      --description "4MOST LRS - 3 labels - Quick APOKASC test." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_quick_3label"

python cannon_test.py --train "hawkins_apokasc_training_set_lrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs" \
                      --description "4MOST LRS - 3 labels - Train on Hawkins(1). Test on Hawkins(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_hawkins_lrs_3label"

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs" \
                      --description "4MOST LRS - 3 labels - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_apokasc_lrs_3label"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband" \
                      --description "4MOST LRS - 3 labels - SNR per band - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_apokasc_lrs_snrperband_3label"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband_noblue" \
                      --description "4MOST LRS - 3 labels - SNR per band + no blue - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_apokasc_lrs_snrperband_noblue_3label"

python cannon_test.py --train "hawkins_apokasc_training_set_hrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs" \
                      --description "4MOST HRS - 3 labels - Train on Hawkins(1). Test on Hawkins(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_hawkins_hrs_3label"

python cannon_test.py --train "4fs_apokasc_training_set_hrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs" \
                      --description "4MOST HRS - 3 labels - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_apokasc_hrs_3label"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband" \
                      --description "4MOST HRS - 3 labels - SNR per band - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_apokasc_hrs_snrperband_3label"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband_noblue" \
                      --description "4MOST HRS - 3 labels - SNR per band + no blue - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_apokasc_hrs_snrperband_noblue_3label"

python cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --description "4MOST HRS - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_hrs_3label"
python cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --description "4MOST LRS - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_lrs_3label"

python cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                      --description "4MOST HRS (censored) - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_3label"
python cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                      --description "4MOST LRS (censored) - 3 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_3label"

python cannon_test.py --train "4fs_ges_dwarf_sample_hrs[SNR=250]" \
                      --test "4fs_ges_dwarfs_perturbed_hrs" \
                      --description "4MOST HRS - 3 labels - Train on GES UVES dwarfs. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ges_dwarfs_perturbed_hrs_3label"
python cannon_test.py --train "4fs_ges_dwarf_sample_lrs[SNR=250]" \
                      --test "4fs_ges_dwarfs_perturbed_lrs" \
                      --description "4MOST LRS - 3 labels - Train on GES UVES dwarfs. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ges_dwarfs_perturbed_lrs_3label"

python cannon_test.py --train "4fs_marcs_grid_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --description "4MOST HRS - 3 labels - Train on MARCS grid. Test on perturbed GES UVES AHM2017." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_marcs_ahm2017_hrs_3label"
python cannon_test.py --train "4fs_marcs_grid_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --description "4MOST LRS - 3 labels - Train on MARCS grid. Test on perturbed GES UVES AHM2017." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_marcs_ahm2017_lrs_3label"

python cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                      --test "4fs_marcs_grid_hrs" \
                      --description "4MOST HRS - 3 labels - Train on GES UVES AHM2017. Test on MARCS grid." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ahm2017_marcs_hrs_3label"
python cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                      --test "4fs_marcs_grid_lrs" \
                      --description "4MOST LRS - 3 labels - Train on GES UVES AHM2017. Test on MARCS grid." \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon/cannon_ahm2017_marcs_lrs_3label"


# -----------------------------------------------------------------------------------------

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250,4800<Teff<9999]" \
                      --test "4fs_apokasc_test_set_lrs[4900<Teff<9999]" \
                      --description "4MOST LRS - 10 labels - Quick APOKASC test." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_quick_10label"

python cannon_test.py --train "hawkins_apokasc_training_set_lrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs" \
                      --description "4MOST LRS - 10 labels - Train on Hawkins(1). Test on Hawkins(2)." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_hawkins_lrs_10label"

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs" \
                      --description "4MOST LRS - 10 labels - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_apokasc_lrs_10label"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband" \
                      --description "4MOST LRS - 10 labels - SNR per band - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_apokasc_lrs_snrperband_10label"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband_noblue" \
                      --description "4MOST LRS - 10 labels - SNR per band + no blue - Train on APOKASC(1). Test on APOKASC(2)." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_apokasc_lrs_snrperband_noblue_10label"

python cannon_test.py --train "hawkins_apokasc_training_set_hrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs" \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_hawkins_hrs_10label"

python cannon_test.py --train "4fs_apokasc_training_set_hrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs" \
                      --description "4MOST HRS - 10 labels - Train on Hawkins(1). Test on Hawkins(2)." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_apokasc_hrs_10label"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband" \
                      --description "4MOST HRS - 10 labels - SNR per band - Train on Hawkins(1). Test on Hawkins(2)." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_apokasc_hrs_snrperband_10label"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband_noblue" \
                      --description "4MOST HRS - 10 labels - SNR per band + no blue - Train on Hawkins(1). Test on Hawkins(2)." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_apokasc_hrs_snrperband_noblue_10label"

python cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --description "4MOST HRS - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_hrs_10label"
python cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --description "4MOST LRS - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_lrs_10label"

python cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                      --description "4MOST HRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_10label"
python cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                      --description "4MOST LRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_10label"

python cannon_test.py --train "4fs_ges_dwarf_sample_hrs[SNR=250]" \
                      --test "4fs_ges_dwarfs_perturbed_hrs" \
                      --description "4MOST HRS - 10 labels - Train on GES UVES dwarfs. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_ges_dwarfs_perturbed_hrs_10label"
python cannon_test.py --train "4fs_ges_dwarf_sample_lrs[SNR=250]" \
                      --test "4fs_ges_dwarfs_perturbed_lrs" \
                      --description "4MOST LRS - 10 labels - Train on GES UVES dwarfs. Test on perturbed version." \
                      --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                      --assume-scaled-solar \
                      --output-file "../output_data/cannon/cannon_ges_dwarfs_perturbed_lrs_10label"

# All stellar labels set of GES stars
# logg, [Nd/H], [O/H], [Mg/H], [V/H], [Ba/H], [Al/H], [Ca/H], [Mn/H], [S/H], [Sc/H], [Ce/H], [Ti/H], [Na/H], [Si/H], [La/H], [Ni/H], [C/H], [Zn/H], [Fe/H], [Co/H], [Cr/H], Teff
