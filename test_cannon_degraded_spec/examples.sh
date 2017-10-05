python cannon_test.py --train "hawkins_apokasc_training_set_lrs[SNR=250]" --test "hawkins_apokasc_test_set_lrs" --output-file "../output_data/cannon_test_hawkins_lrs"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband[SNR=250]" --test "hawkins_apokasc_test_set_lrs_snrperband" --output-file "../output_data/cannon_test_hawkins_lrs_snrperband"
python cannon_test.py --train "hawkins_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" --test "hawkins_apokasc_test_set_lrs_snrperband_noblue" --output-file "../output_data/cannon_test_hawkins_lrs_snrperband_noblue"

python cannon_test.py --train "4fs_apokasc_training_set_lrs[SNR=250]" --test "4fs_apokasc_test_set_lrs" --output-file "../output_data/cannon_test_4fs_lrs"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband[SNR=250]" --test "4fs_apokasc_test_set_lrs_snrperband" --output-file "../output_data/cannon_test_4fs_lrs_snrperband"
python cannon_test.py --train "4fs_apokasc_training_set_lrs_snrperband_noblue[SNR=250]" --test "4fs_apokasc_test_set_lrs_snrperband_noblue" --output-file "../output_data/cannon_test_4fs_lrs_snrperband_noblue"

python cannon_test.py --train "hawkins_apokasc_training_set_hrs[SNR=250]" --test "hawkins_apokasc_test_set_hrs" --output-file "../output_data/cannon_test_hawkins_hrs"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband[SNR=250]" --test "hawkins_apokasc_test_set_hrs_snrperband" --output-file "../output_data/cannon_test_hawkins_hrs_snrperband"
python cannon_test.py --train "hawkins_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" --test "hawkins_apokasc_test_set_hrs_snrperband_noblue" --output-file "../output_data/cannon_test_hawkins_hrs_snrperband_noblue"

python cannon_test.py --train "4fs_apokasc_training_set_hrs[SNR=250]" --test "4fs_apokasc_test_set_hrs" --output-file "../output_data/cannon_test_4fs_hrs"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband[SNR=250]" --test "4fs_apokasc_test_set_hrs_snrperband" --output-file "../output_data/cannon_test_4fs_hrs_snrperband"
python cannon_test.py --train "4fs_apokasc_training_set_hrs_snrperband_noblue[SNR=250]" --test "4fs_apokasc_test_set_hrs_snrperband_noblue" --output-file "../output_data/cannon_test_4fs_hrs_snrperband_noblue"

python cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250]" --test "4fs_ahm2017_perturbed_hrs" --output-file "../output_data/cannon_ahm2017_perturbed_hrs"
python cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250]" --test "4fs_ahm2017_perturbed_lrs" --output-file "../output_data/cannon_ahm2017_perturbed_lrs"

python cannon_test.py --train "4fs_ges_dwarf_sample_hrs[SNR=250]" --test "4fs_ges_dwarfs_perturbed_hrs" --output-file "../output_data/cannon_ges_dwarfs_perturbed_hrs"
python cannon_test.py --train "4fs_ges_dwarf_sample_lrs[SNR=250]" --test "4fs_ges_dwarfs_perturbed_lrs" --output-file "../output_data/cannon_ges_dwarfs_perturbed_lrs"

python cannon_test.py --train "4fs_ges_marcs_grid_hrs[SNR=250]" --test "4fs_ahm2017_perturbed_hrs" --output-file "../output_data/cannon_marcs_ahm2017_hrs"
python cannon_test.py --train "4fs_ges_marcs_grid_lrs[SNR=250]" --test "4fs_ahm2017_perturbed_lrs" --output-file "../output_data/cannon_marcs_ahm2017_lrs"

