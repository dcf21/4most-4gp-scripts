#!/bin/bash

# Produce plots of the precision of labels as a function of the radial velocity which was injected into the test spectra

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
../../../../output_data/cannon/cannon_galah_withrv_censored_snr150_hrs_10label \
../../../../output_data/cannon/cannon_galah_withrv_censored_snr150_lrs_10label \
../../../../output_data/cannon/cannon_galah_withrv_censored_snr50_hrs_10label \
../../../../output_data/cannon/cannon_galah_withrv_censored_snr50_lrs_10label

do
    run_name=`echo ${run} | sed 's@../../../../output_data/cannon/cannon_\(.*\)$@\1@'`
    run_name=`echo ${run_name} | sed 's@_withrv_censored@@g'`
    run_name=`echo ${run_name} | sed 's@_10label@@g'`

    run_name_escaped=`echo ${run_name} | sed 's@_@\\\\_@g'`


    # Plot abundance over H and over Fe
    for divisor in "h" # "fe"
    do
        # Plots averaging the Cannon's performance over stars of all types and metallicities
        python3 offset_rms.py \
          --abscissa "rv" \
          --abundances-over-${divisor} \
          --cannon-output "${run}" --dataset-label "${run_name_escaped}" --dataset-colour "green" \
          --output "../../../../output_plots/cannon_performance/performance_vs_label/comparison_withrv_${run_name}_${divisor}" &

        # Break down the Cannon's performance by the type of star
        python3 offset_rms.py \
          --abscissa "rv" \
          --abundances-over-${divisor} \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<0.5;[Fe/H]>0" --dataset-label "${run_name_escaped}; Giants \$0<\\mathrm{[Fe/H]}\$" --dataset-colour "blue" --dataset-line-type 1 \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<0;[Fe/H]>-0.5" --dataset-label "${run_name_escaped}; Giants \$-0.5<\\mathrm{[Fe/H]}<0\$" --dataset-colour "red" --dataset-line-type 1 \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<-0.5;[Fe/H]>-1" --dataset-label "${run_name_escaped}; Giants \$-1<\\mathrm{[Fe/H]}<-0.5\$" --dataset-colour "green" --dataset-line-type 1 \
          --cannon-output "${run}" --dataset-filter "logg<3.25;[Fe/H]<-1;[Fe/H]>-3" --dataset-label "${run_name_escaped}; Giants \$\\mathrm{[Fe/H]}<-1\$" --dataset-colour "orange" --dataset-line-type 1 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<0.5;[Fe/H]>0" --dataset-label "${run_name_escaped}; Dwarfs \$0<\\mathrm{[Fe/H]}\$" --dataset-colour "blue" --dataset-line-type 2 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<0;[Fe/H]>-0.5" --dataset-label "${run_name_escaped}; Dwarfs \$-0.5<\\mathrm{[Fe/H]}<0\$" --dataset-colour "red" --dataset-line-type 2 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<-0.5;[Fe/H]>-1" --dataset-label "${run_name_escaped}; Dwarfs \$-1<\\mathrm{[Fe/H]}<-0.5\$" --dataset-colour "green" --dataset-line-type 2 \
          --cannon-output "${run}" --dataset-filter "logg>3.25;[Fe/H]<-1;[Fe/H]>-3" --dataset-label "${run_name_escaped}; Dwarfs \$\\mathrm{[Fe/H]}<-1\$" --dataset-colour "orange" --dataset-line-type 2 \
          --output "../../../../output_plots/cannon_performance/performance_vs_label/comparison_withrv_by_type_${run_name}_${divisor}" &
    done
    wait
done
