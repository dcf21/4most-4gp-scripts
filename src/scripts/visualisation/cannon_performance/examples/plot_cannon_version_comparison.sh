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

for mode in hrs lrs
do
    for script in offset_rms.py
    do
        python3 ${script} \
        --cannon-output ../../../../output_data/cannon/cannon_galah_${mode}_3label \
        --dataset-label "Casey 2017" \
        --cannon-output ../../../../output_data/cannon/new_cannon_galah_${mode}_3label \
        --dataset-label "Casey 2018" \
        --cannon-output ../../../../output_data/cannon/annaho_cannon_galah_${mode}_3label \
        --dataset-label "Ho" \
        --output ../../../../output_plots/cannon_performance/compare_cannon_versions/test1_${mode}_3label &

        for label_count in 3 10
        do
            for censored in "" "_censored"
            do
                python3 ${script} \
                --cannon-output ../../../../output_data/cannon/cannon_galah${censored}_${mode}_${label_count}label \
                --dataset-label "Casey 2017" \
                --cannon-output ../../../../output_data/cannon/new_cannon_galah${censored}_${mode}_${label_count}label \
                --dataset-label "Casey 2018" \
                --output ../../../../output_plots/cannon_performance/compare_cannon_versions/test2${censored}_${mode}_${label_count}label &
            done
            wait
         done

    done
done
