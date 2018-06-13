#!/bin/bash

source ../../../virtualenv/bin/activate

# Create directories where plots get held
mkdir -p ../../output_plots/cannon_performance/arrows
mkdir -p ../../output_plots/cannon_performance/performance_vs_label
mkdir -p ../../output_plots/cannon_performance/uncertainties
mkdir -p ../../output_plots/cannon_performance/required_snrA
mkdir -p ../../output_plots/cannon_performance/required_snrB
mkdir -p ../../output_plots/cannon_performance/label_offsets

# comparison_censoring_schemes_*
# Create plots of the relative performance of the 4 censoring schemes, trained and tested on UVES or GALAH
for mode in lrs hrs
do
    for run in "ahm2017_perturbed" "galah"
    do
        python2.7 mean_performance_vs_label.py \
          --plot-width 14 --hide-date \
          --cannon-output "../../output_data/cannon/cannon_${run}_${mode}_10label.json" --dataset-label "No censoring" --dataset-colour "green" \
          --cannon-output "../../output_data/cannon/cannon_${run}_censored_${mode}_10label.json" --dataset-label "Censoring scheme 1" --dataset-colour "blue" \
          --cannon-output "../../output_data/cannon/cannon_${run}_censored2_${mode}_10label.json" --dataset-label "Censoring scheme 2" --dataset-colour "red" \
          --cannon-output "../../output_data/cannon/cannon_${run}_censored3_${mode}_10label.json" --dataset-label "Censoring scheme 3" --dataset-colour "purple" \
          --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_censoring_schemes_${run}_${mode}" &
    done
done
wait

# comparison_low_z_*
# Create a plot of the performance of the Cannon, when trained and tested on the [Fe/H] < -1 and [Fe/H] > 1 regimes separately
for mode in lrs hrs
do
    for run in "ahm2017_perturbed" "galah"
    do
        python2.7 mean_performance_vs_label.py \
          --plot-width 14 --hide-date \
          --cannon-output "../../output_data/cannon/cannon_${run}_fehcut2_${mode}_10label.json" --dataset-filter "[Fe/H]<-1" --dataset-label "Trained \$z<-1\$ only" --dataset-colour "green" \
          --cannon-output "../../output_data/cannon/cannon_${run}_${mode}_10label.json" --dataset-filter "[Fe/H]<-1" --dataset-label "Trained on full sample" --dataset-colour "red" \
          --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_low_z_${run}_${mode}" &
    done
done
wait

# comparisonA -- Plot the performance of the Cannon for different types of stars -- giants and dwarfs, metal rich and metal poor
for mode in lrs hrs
do
    # Plot for both AHM2017 and GALAH datasets
    for sample in "ahm2017_perturbed" "galah"
    do
        # Plot performance for abundances over both H and Fe
        for divisor in "h" "fe"
        do
            python2.7 mean_performance_vs_label.py \
              --plot-width 14 --hide-date \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>0;[Fe/H]<1" --dataset-label "Giants; [Fe/H]\$>0\$" --dataset-colour "purple" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>0;[Fe/H]<1" --dataset-label "Dwarfs; [Fe/H]\$>0\$" --dataset-colour "magenta" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>-0.5;[Fe/H]<0" --dataset-label "Giants; \$-0.5<\$[Fe/H]\$<0\$" --dataset-colour "blue" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>-0.5;[Fe/H]<0" --dataset-label "Dwarfs; \$-0.5<\$[Fe/H]\$<0\$" --dataset-colour "red" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>-1;[Fe/H]<-0.5" --dataset-label "Giants; \$-1<\$[Fe/H]$<-0.5$" --dataset-colour "cyan" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>-1;[Fe/H]<-0.5" --dataset-label "Dwarfs; \$-1<\$[Fe/H]$<-0.5$" --dataset-colour "orange" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>-2;[Fe/H]<-1" --dataset-label "Giants; [Fe/H]$<-1$" --dataset-colour "green" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>-2;[Fe/H]<-1" --dataset-label "Dwarfs; [Fe/H]$<-1$" --dataset-colour "brown" --dataset-linetype 1 \
              --abundances-over-${divisor} \
              --output-file "../../output_plots/cannon_performance/performance_vs_label/comparisonA_${sample}_${mode}_${divisor}" &
        done
    done
    wait
done

# comparisonB -- Plot the performance of the Cannon when fitting 3 or 10 parameters
for mode in lrs hrs
do
    # Plot for both AHM2017 and GALAH datasets
    for sample in "galah"
    do
        for divisor in "h" "fe"
        do

            python2.7 mean_performance_vs_label.py \
              --cannon-output "../../output_data/cannon/cannon_${sample}_${mode}_3label.json" --dataset-label "3 parameter; uncensored" --dataset-colour "green" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_${mode}_4label.json" --dataset-label "4 parameter; uncensored" --dataset-colour "blue" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_${mode}_5label.json" --dataset-label "5 parameter; uncensored" --dataset-colour "orange" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_${mode}_10label.json" --dataset-label "10 parameters; uncensored" --dataset-colour "red" --dataset-linetype 1 \
              --abundances-over-${divisor} \
              --output-file "../../output_plots/cannon_performance/performance_vs_label/comparisonB_${sample}_${mode}_${divisor}" &

            python2.7 mean_performance_vs_label.py \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_3label.json" --dataset-label "3 parameter; censored" --dataset-colour "blue" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_4label.json" --dataset-label "4 parameter; censored" --dataset-colour "green" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_5label.json" --dataset-label "5 parameter; censored" --dataset-colour "orange" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/cannon_${sample}_censored_${mode}_10label.json" --dataset-label "10 parameters; censored" --dataset-colour "red" --dataset-linetype 1 \
              --abundances-over-${divisor} \
              --output-file "../../output_plots/cannon_performance/performance_vs_label/comparisonB_${sample}_${mode}_censored_${divisor}" &

        done
        wait
    done
done

# Now plot performance vs SNR for every Cannon run we have
for cannon_output in ../../output_data/cannon/*.json
do

    # Extract name of Cannon run from filename
    cannon_run=`echo ${cannon_output} | sed 's@../../output_data/cannon/\(.*\).json@\1@g'`

    # Produce a plot of precision vs SNR
    python2.7 mean_performance_vs_label.py \
      --plot-width 14 --hide-date \
      --cannon-output "${cannon_output}" \
      --output-file "../../output_plots/cannon_performance/performance_vs_label/${cannon_run}"

    # Produce a scatter plot of the nominal uncertainties in the Cannon's label estimates
    #python2.7 scatter_plot_cannon_uncertainty.py --cannon-output "${cannon_output}" \
    #  --output-stub "../../output_plots/cannon_performance/uncertainties/${cannon_run}"

    # Now produce scatter plots of the SNR required to achieve the target precision in each label for each star
    for colour_label in "Teff" "logg" "[Fe/H]" "[Ca/H]" "[Mg/H]" "[Ti/H]" "[Si/H]" "[Na/H]" "[Ni/H]" "[Cr/H]"
    do

        # Figure out the target precision for each label, and units
        target_accuracy="0.1"
        if [ "$colour_label" == "Teff" ] ; then target_accuracy="100" ; fi
        if [ "$colour_label" == "logg" ] ; then target_accuracy="0.3" ; fi

        accuracy_unit="dex"
        if [ "$colour_label" == "Teff" ] ; then accuracy_unit="K" ; fi

        # Produce a version of each label which is safe to put in the filename of a file
        path_safe_label=`echo ${colour_label} | sed -e 's@\[\(.*\)/H\]@\1H@g'`

        # required_snrA
        # Scatter plots of required SNR in the Teff / log(g) plane
        python2.7 scatter_plot_snr_required.py --label "Teff{7000:3400}" --label "logg{5:0}" \
          --label-axis-latex "Teff" --label-axis-latex "log(g)" \
          --label-axis-latex "${colour_label}" \
          --colour-by-label "${colour_label}" \
          --target-accuracy "${target_accuracy}" \
          --colour-range-min 30 --colour-range-max 120 \
          --cannon-output "${cannon_output}" \
          --accuracy-unit "${accuracy_unit}" \
          --output-stub "../../output_plots/cannon_performance/required_snrA/${cannon_run}/${path_safe_label}" &

        # required_snrB
        # Scatter plots of required SNR in the metallicity / log(g) plane
        python2.7 scatter_plot_snr_required.py --label "[Fe/H]{1:-3}" --label "logg{5:0}" \
          --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
          --label-axis-latex "${colour_label}" \
          --colour-by-label "${colour_label}" \
          --target-accuracy "${target_accuracy}" \
          --colour-range-min 30 --colour-range-max 120 \
          --cannon-output "${cannon_output}" \
          --accuracy-unit "${accuracy_unit}" \
          --output-stub "../../output_plots/cannon_performance/required_snrB/${cannon_run}/${path_safe_label}" &

        # label_offsets/A_*
        # Scatter plots of the absolute offsets in each label, in the Teff / log(g) plane
        python2.7 scatter_plot_coloured.py --label "Teff{7000:3400}" --label "logg{5:0}" \
          --label-axis-latex "Teff" --label-axis-latex "log(g)" \
          --label-axis-latex "${colour_label}" \
          --colour-by-label "${colour_label}{:}" \
          --colour-range-min " -$(python2.7 -c "print ${target_accuracy}*3")" \
          --colour-range-max " $(python2.7 -c "print ${target_accuracy}*3")" \
          --cannon-output "${cannon_output}" \
          --output-stub "../../output_plots/cannon_performance/label_offsets/${cannon_run}/A_${path_safe_label}" &

        # label_offsets/B_*
        # Scatter plots of the absolute offsets in each label, in the [Fe/H] / log(g) plane
        python2.7 scatter_plot_coloured.py --label "[Fe/H]{1:-3}" --label "logg{5:0}" \
          --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
          --label-axis-latex "${colour_label}" \
          --colour-by-label "${colour_label}{:}" \
          --colour-range-min " -$(python2.7 -c "print ${target_accuracy}*3")" \
          --colour-range-max " $(python2.7 -c "print ${target_accuracy}*3")" \
          --cannon-output "${cannon_output}" \
          --output-stub "../../output_plots/cannon_performance/label_offsets/${cannon_run}/B_${path_safe_label}" &

       # Wait for this batch of plots to finish
       wait
    done
done

