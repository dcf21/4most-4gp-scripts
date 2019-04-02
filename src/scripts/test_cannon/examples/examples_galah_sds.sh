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

python3 cannon_test.py --train "4fs_synthetic_dwarf_sample_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 10 labels - Train on SDS. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_sds_hrs_10label"
python3 cannon_test.py --train "4fs_synthetic_dwarf_sample_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 10 labels - Train on SDS. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_sds_lrs_10label"

python3 cannon_test.py --train "4fs_synthetic_dwarf_sample_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 10 labels - Train on SDS. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_sds_censored_hrs_10label"
python3 cannon_test.py --train "4fs_synthetic_dwarf_sample_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 10 labels - Train on SDS. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_sds_censored_lrs_10label"

# -----------------------------------------------------------------------------------------

python3 cannon_test.py --train "4fs_synthetic_dwarf_sample_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --continuum-normalisation "running_mean" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 10 labels - Train on SDS. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_sds_censored_hrs_cn_10label"
python3 cannon_test.py --train "4fs_synthetic_dwarf_sample_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --continuum-normalisation "running_mean" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 10 labels - Train on SDS. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_sds_censored_lrs_cn_10label"


