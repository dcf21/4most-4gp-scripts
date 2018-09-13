#!/bin/bash

# Produce plots of the precision of labels as a function of reddening, at fixed
# SNR

# ---

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../../virtualenv/bin/activate

for kernel in gaussian half_ellipse
do

    for mode in hrs lrs
    do

        for snr in 20 50
        do

            python2.7 concatenate_cannon_runs.py \
            --output-file ../../../../output_data/cannon/cannon_galah_${kernel}_all_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.2_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.3_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.4_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.5_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.6_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.7_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.8_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_1.9_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_2.0_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_2.1_censored_${mode}_10label_snr${snr} \
            --input-file ../../../../output_data/cannon/cannon_galah_${kernel}_2.2_censored_${mode}_10label_snr${snr}

        done
    done
done

