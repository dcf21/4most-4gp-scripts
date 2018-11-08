#!/bin/bash

# Produce plots of the comparative precision of three different versions of the Cannon, by Andy Casey and Anna Ho

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
        for label_count in 3 5 10
        do
            python3 ${script} \
            --cannon-output ../../../../output_data/cannon/cannon_galah_${mode}_${label_count}label \
            --dataset-label "Casey 2017" \
            --cannon-output ../../../../output_data/cannon/new_cannon_galah_${mode}_${label_count}label \
            --dataset-label "Casey 2018" \
            --cannon-output ../../../../output_data/cannon/annaho_cannon_galah_${mode}_${label_count}label \
            --dataset-label "Ho" \
            --output ../../../../output_plots/cannon_performance/compare_cannon_versions/test1_${mode}_${label_count}label &

            # Anna Ho's code doesn't support censoring, or 10 labels fits, so also produce plots without Anna's Cannon
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

