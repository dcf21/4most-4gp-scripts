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

# ---

# Create directories where plots get held
mkdir -p ../../../../output_plots/cannon_performance/performance_vs_label

# Loop over all the Cannon runs we have
for run in \
../../../../output_data/cannon/cannon_galah_reddened_censored_snr50_hrs_10label.json \
../../../../output_data/cannon/cannon_galah_reddened_censored_snr50_hrs_cn_10label.json \
../../../../output_data/cannon/cannon_galah_reddened_censored_snr50_lrs_10label.json \
../../../../output_data/cannon/cannon_galah_reddened_censored_snr50_lrs_cn_10label.json \

do
    run_name=`echo ${run} | sed 's@../../../../output_data/cannon/cannon_\(.*\).json@\1@'`
    run_name=`echo ${run_name} | sed 's@_reddened_censored@@g'`
    run_name=`echo ${run_name} | sed 's@_10label@@g'`

    run_name_escaped=`echo ${run_name} | sed 's@_@\\\\_@g'`


    # Plot abundance over H and over Fe
    for divisor in "h" "fe"
    do
        # Plots averaging the Cannon's performance over stars of all types and metallicities
        python3 mean_performance_vs_label.py \
          --plot-width 14 --hide-date \
          --abscissa "ebv" \
          --abundances-over-${divisor} \
          --cannon-output "${run}" --dataset-label "${run_name_escaped}" --dataset-colour "green" \
          --output-file "../../../../output_plots/cannon_performance/performance_vs_label/comparison_reddening_${run_name}_${divisor}" &

        # Break down the Cannon's performance by the type of star
        python3 mean_performance_vs_label.py \
          --plot-width 14 --hide-date \
          --abscissa "ebv" \
          --abundances-over-${divisor} \
          --plot-width 24 \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<0.5;[Fe/H]>0" --dataset-label "${run_name_escaped}; Giants \$0<\\mathrm{[Fe/H]}\$" --dataset-colour "blue" --dataset-linetype 1 \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<0;[Fe/H]>-0.5" --dataset-label "${run_name_escaped}; Giants \$-0.5<\\mathrm{[Fe/H]}<0\$" --dataset-colour "red" --dataset-linetype 1 \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<-0.5;[Fe/H]>-1" --dataset-label "${run_name_escaped}; Giants \$-1<\\mathrm{[Fe/H]}<-0.5\$" --dataset-colour "green" --dataset-linetype 1 \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<-1;[Fe/H]>-3" --dataset-label "${run_name_escaped}; Giants \$\\mathrm{[Fe/H]}<-1\$" --dataset-colour "orange" --dataset-linetype 1 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<0.5;[Fe/H]>0" --dataset-label "${run_name_escaped}; Dwarfs \$0<\\mathrm{[Fe/H]}\$" --dataset-colour "blue" --dataset-linetype 2 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<0;[Fe/H]>-0.5" --dataset-label "${run_name_escaped}; Dwarfs \$-0.5<\\mathrm{[Fe/H]}<0\$" --dataset-colour "red" --dataset-linetype 2 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<-0.5;[Fe/H]>-1" --dataset-label "${run_name_escaped}; Dwarfs \$-1<\\mathrm{[Fe/H]}<-0.5\$" --dataset-colour "green" --dataset-linetype 2 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<-1;[Fe/H]>-3" --dataset-label "${run_name_escaped}; Dwarfs \$\\mathrm{[Fe/H]}<-1\$" --dataset-colour "orange" --dataset-linetype 2 \
          --output-file "../../../../output_plots/cannon_performance/performance_vs_label/comparison_reddening_by_type_${run_name}_${divisor}" &
    done
    wait
done


# Loop over all the Cannon runs we have
for run in \
../../../../output_data/cannon/cannon_galah_giants_reddened_censored_snr50_s4grn_hrs_10label.json \
../../../../output_data/cannon/cannon_galah_giants_reddened_censored_snr50_s4red_hrs_10label.json \
../../../../output_data/cannon/cannon_galah_turnoff_reddened_censored_snr50_s4grn_hrs_10label.json \
../../../../output_data/cannon/cannon_galah_turnoff_reddened_censored_snr50_s4red_hrs_10label.json \

do
    run_name=`echo ${run} | sed 's@../../../../output_data/cannon/cannon_\(.*\).json@\1@'`
    run_name=`echo ${run_name} | sed 's@_reddened_censored@@g'`
    run_name=`echo ${run_name} | sed 's@_10label@@g'`

    run_name_escaped=`echo ${run_name} | sed 's@_@\\\\_@g'`

    # Plot abundance over H and over Fe
    for divisor in "h" "fe"
    do
        # Plots averaging the Cannon's performance over stars of all types and metallicities
        python3 mean_performance_vs_label.py \
          --plot-width 14 --hide-date \
          --abscissa "ebv" \
          --abundances-over-${divisor} \
          --cannon-output "${run}" --dataset-label "${run_name_escaped}" --dataset-colour "green" \
          --output-file "../../../../output_plots/cannon_performance/performance_vs_label/comparison_reddening_${run_name}_${divisor}" &
    done
    wait
done
