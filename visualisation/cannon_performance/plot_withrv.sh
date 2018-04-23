#!/bin/bash

# Produce plots of the precision of labels as a function of reddening, at fixed SNR

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots/cannon_performance/performance_vs_label

# Loop over all the Cannon runs we have
for run in \
../../output_data/cannon/cannon_galah_withrv_censored_snr50_hrs_10label.json \
../../output_data/cannon/cannon_galah_withrv_censored_snr50_lrs_10label.json

do
    run_name=`echo ${run} | sed 's@../../output_data/cannon/cannon_\(.*\).json@\1@'`
    run_name=`echo ${run_name} | sed 's@_withrv_censored@@g'`
    run_name=`echo ${run_name} | sed 's@_10label@@g'`

    run_name_escaped=`echo ${run_name} | sed 's@_@\\\\_@g'`


    # Plot abundance over H and over Fe
    for divisor in "h" "fe"
    do
        # Plots averaging the Cannon's performance over stars of all types and metallicities
        python2.7 mean_performance_vs_label.py \
          --abscissa "rv" \
          --abundances-over-${divisor} \
          --cannon-output "${run}" --dataset-label "${run_name_escaped}" --dataset-colour "green" \
          --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_withrv_${run_name}_${divisor}" &

        # Break down the Cannon's performance by the type of star
        python2.7 mean_performance_vs_label.py \
          --abscissa "rv" \
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
          --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_withrv_by_type_${run_name}_${divisor}" &
    done
    wait
done
