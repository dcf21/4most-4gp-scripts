#!/bin/bash

# Produce plots of the precision of labels as a function of reddening, at fixed SNR

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots/cannon_performance/performance_vs_label

# Show plots for both LRS and HRS
for mode in lrs hrs
do
    # Plot abundance over H and over Fe
    for divisor in "h" "fe"
    do
        # Plots averaging the Cannon's performance over stars of all types and metallicities
        python2.7 mean_performance_vs_label.py \
          --abscissa "ebv" \
          --abundances-over-${divisor} \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-label "${mode}" --dataset-colour "green" \
          --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_reddening_${mode}_${divisor}"

        # Break down the Cannon's performance by the type of star
        python2.7 mean_performance_vs_label.py \
          --abscissa "ebv" \
          --abundances-over-${divisor} \
          --plot-width 24 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]<0.5;[Fe/H]>0" --dataset-label "${mode}; Giants \$0<\\mathrm{[Fe/H]}\$" --dataset-colour "blue" --dataset-linetype 1 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]<0;[Fe/H]>-0.5" --dataset-label "${mode}; Giants \$-0.5<\\mathrm{[Fe/H]}<0\$" --dataset-colour "red" --dataset-linetype 1 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]<-0.5;[Fe/H]>-1" --dataset-label "${mode}; Giants \$-1<\\mathrm{[Fe/H]}<-0.5\$" --dataset-colour "green" --dataset-linetype 1 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]<-1;[Fe/H]>-3" --dataset-label "${mode}; Giants \$\\mathrm{[Fe/H]}<-1\$" --dataset-colour "orange" --dataset-linetype 1 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]<0.5;[Fe/H]>0" --dataset-label "${mode}; Dwarfs \$0<\\mathrm{[Fe/H]}\$" --dataset-colour "blue" --dataset-linetype 2 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]<0;[Fe/H]>-0.5" --dataset-label "${mode}; Dwarfs \$-0.5<\\mathrm{[Fe/H]}<0\$" --dataset-colour "red" --dataset-linetype 2 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]<-0.5;[Fe/H]>-1" --dataset-label "${mode}; Dwarfs \$-1<\\mathrm{[Fe/H]}<-0.5\$" --dataset-colour "green" --dataset-linetype 2 \
          --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]<-1;[Fe/H]>-3" --dataset-label "${mode}; Dwarfs \$\\mathrm{[Fe/H]}<-1\$" --dataset-colour "orange" --dataset-linetype 2 \
          --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_reddening_by_type_${mode}_${divisor}"
    done
done

