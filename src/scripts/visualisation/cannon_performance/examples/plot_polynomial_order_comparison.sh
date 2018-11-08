#!/bin/bash

# Produce plots of the comparative precision of Cannons which fit 2nd, 3rd and 4th order polynomials
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
        for label_count in 3 5
        do
            for censored in "" "_censored"
            do
                python3 ${script} \
                --cannon-output ../../../../output_data/cannon/cannon_galah${censored}_${mode}_${label_count}label \
                --dataset-label "2nd order" \
                --cannon-output ../../../../output_data/cannon/cannon_cubic_galah${censored}_${mode}_${label_count}label \
                --dataset-label "3rd order" \
                --cannon-output ../../../../output_data/cannon/cannon_quartic_galah${censored}_${mode}_${label_count}label \
                --dataset-label "4th order" \
                --output ../../../../output_plots/cannon_performance/compare_polynomial_orders/${mode}${censored}_${label_count}label &
            done
        done
        wait
    done
done
