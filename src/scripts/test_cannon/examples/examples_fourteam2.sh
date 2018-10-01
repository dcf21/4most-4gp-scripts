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

python3 cannon_test.py --train "4fs_ahm2017_sample_250only_hrs[SNR=250]" \
                       --test "4fs_reddened_fourteam2_sample_hrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST HRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on 4TEAM2." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_reddened_fourteam2_sample_hrs_10label"
python3 cannon_test.py --train "4fs_ahm2017_sample_250only_lrs[SNR=250]" \
                       --test "4fs_reddened_fourteam2_sample_lrs" \
                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                       --description "4MOST LRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on 4TEAM2." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_reddened_fourteam2_sample_lrs_10label"

# All stellar labels set of GES stars
# logg, [Nd/H], [O/H], [Mg/H], [V/H], [Ba/H], [Al/H], [Ca/H], [Mn/H], [S/H], [Sc/H], [Ce/H], [Ti/H], [Na/H], [Si/H], [La/H], [Ni/H], [C/H], [Zn/H], [Fe/H], [Co/H], [Cr/H], Teff
