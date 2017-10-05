#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python cannon_test.py --train "hawkins_apokasc_training_set_lrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs_snrperband"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs_snrperband_noblue"

python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs_snrperband"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs_snrperband_noblue"

python cannon_test.py --train "hawkins_apokasc_training_set_hrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs_snrperband"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs_snrperband_noblue"

python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs_snrperband"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs_snrperband_noblue"

python cannon_test.py --train "4fs_ges_marcs_grid_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_marcs_ahm2017_hrs"
python cannon_test.py --train "4fs_ges_marcs_grid_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H],[Ca/H]" \
                      --output-file "../output_data/cannon_marcs_ahm2017_lrs"

# All stellar labels set of GES stars
# logg, [Nd/H], [O/H], [Mg/H], [V/H], [Ba/H], [Al/H], [Ca/H], [Mn/H], [S/H], [Sc/H], [Ce/H], [Ti/H], [Na/H], [Si/H], [La/H], [Ni/H], [C/H], [Zn/H], [Fe/H], [Co/H], [Cr/H], Teff
