#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250,4800<Teff<9999]" \
                      --test "4fs_apokasc_test_set_lrs[4900<Teff<9999]" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_quick_3label"

python cannon_test.py --train "hawkins_apokasc_training_set_lrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs_3label"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs_snrperband" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs_snrperband_3label"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs_snrperband_noblue_3label"

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs_3label"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs_snrperband_3label"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs_snrperband_noblue_3label"

python cannon_test.py --train "hawkins_apokasc_training_set_hrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs_3label"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs_snrperband" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs_snrperband_3label"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs_snrperband_noblue_3label"

python cannon_test.py --train "4fs_apokasc_training_set_hrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs_3label"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs_snrperband_3label"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs_snrperband_noblue_3label"


# -----------------------------------------------------------------------------------------

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250,4800<Teff<9999]" \
                      --test "4fs_apokasc_test_set_lrs[4900<Teff<9999]" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_quick"

python cannon_test.py --train "hawkins_apokasc_training_set_lrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs_snrperband"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "hawkins_apokasc_test_set_lrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_hawkins_lrs_snrperband_noblue"

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs_snrperband"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_lrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_apokasc_lrs_snrperband_noblue"

python cannon_test.py --train "hawkins_apokasc_training_set_hrs[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs_snrperband"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "hawkins_apokasc_test_set_hrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_hawkins_hrs_snrperband_noblue"

python cannon_test.py --train "4fs_apokasc_training_set_hrs[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs_snrperband"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" \
                      --test "4fs_apokasc_test_set_hrs_snrperband_noblue" \
                      --labels "Teff,logg,[Fe/H],[C/H],[N/H],[O/H],[Na/H],[Mg/H],[Al/H],[Si/H]" \
                      --output-file "../output_data/cannon_apokasc_hrs_snrperband_noblue"

python cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_ahm2017_perturbed_hrs"
python cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_ahm2017_perturbed_lrs"

python cannon_test.py --train "4fs_ges_dwarf_sample_hrs[SNR=250]" \
                      --test "4fs_ges_dwarfs_perturbed_hrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_ges_dwarfs_perturbed_hrs"
python cannon_test.py --train "4fs_ges_dwarf_sample_lrs[SNR=250]" \
                      --test "4fs_ges_dwarfs_perturbed_lrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_ges_dwarfs_perturbed_lrs"

python cannon_test.py --train "4fs_marcs_grid_hrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_hrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_marcs_ahm2017_hrs"
python cannon_test.py --train "4fs_marcs_grid_lrs[SNR=250]" \
                      --test "4fs_ahm2017_perturbed_lrs" \
                      --labels "Teff,logg,[Fe/H]" \
                      --output-file "../output_data/cannon_marcs_ahm2017_lrs"

# All stellar labels set of GES stars
# logg, [Nd/H], [O/H], [Mg/H], [V/H], [Ba/H], [Al/H], [Ca/H], [Mn/H], [S/H], [Sc/H], [Ce/H], [Ti/H], [Na/H], [Si/H], [La/H], [Ni/H], [C/H], [Zn/H], [Fe/H], [Co/H], [Cr/H], Teff
