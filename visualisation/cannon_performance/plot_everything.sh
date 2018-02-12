#!/bin/bash

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots/cannon_performance/arrows
mkdir -p ../../output_plots/cannon_performance/performance_vs_label
mkdir -p ../../output_plots/cannon_performance/uncertainties
mkdir -p ../../output_plots/cannon_performance/required_snrA
mkdir -p ../../output_plots/cannon_performance/required_snrB
mkdir -p ../../output_plots/cannon_performance/label_offsets

for mode in lrs hrs
do

for run in "" "_LiBa" "_CO"
do

python2.7 mean_performance_vs_label.py \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_${mode}_10label${run}.json" --dataset-label "No censoring" --dataset-colour "green" \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored_${mode}_10label${run}.json" --dataset-label "Censoring scheme 1" --dataset-colour "blue" \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored2_${mode}_10label${run}.json" --dataset-label "Censoring scheme 2" --dataset-colour "red" \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored3_${mode}_10label${run}.json" --dataset-label "Censoring scheme 3" --dataset-colour "purple" \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_censoring_schemes_${mode}${run}"

done

python2.7 mean_performance_vs_label.py \
  --abscissa "ebv" \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_reddened_censored_${mode}_10label.json" --dataset-label "Reddened ${mode}" --dataset-colour "green" \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_reddening_${mode}"

python2.7 mean_performance_vs_label.py \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_fehcut2_${mode}_10label.json" --dataset-filter "[Fe/H]<-1" --dataset-label "Trained \$z<-1\$ only (UVES)" --dataset-colour "green" \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_fehcut2b_${mode}_10label.json" --dataset-filter "[Fe/H]<-1" --dataset-label "Trained \$z<-1\$ only (GALAH)" --dataset-colour "blue" \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_${mode}_10label.json" --dataset-filter "[Fe/H]<-1" --dataset-label "Trained on full UVES sample" --dataset-colour "red" \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_low_z_${mode}"

done

python2.7 scatter_plot_arrows.py --output-stub "../../output_plots/cannon_performance/arrows/apokasc_teff_logg_hrs_offset_arrows" \
  --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
  --label-axis-latex "Teff" --label-axis-latex "log(g)" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_10label.json"

python2.7 scatter_plot_arrows.py --output-stub "../../output_plots/cannon_performance/arrows/apokasc_teff_logg_lrs_offset_arrows" \
  --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
  --label-axis-latex "Teff" --label-axis-latex "log(g)" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_10label.json"

python2.7 mean_performance_vs_label.py \
  --cannon-output "../../output_data/cannon/cannon_hawkins_lrs_10label.json" --dataset-label "Hawkins LRS" \
  --cannon-output "../../output_data/cannon/cannon_hawkins_hrs_10label.json" --dataset-label "Hawkins HRS" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_10label.json" --dataset-label "Ford LRS" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_10label.json" --dataset-label "Ford HRS" \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_apokasc_hawkins"

#python2.7 mean_performance_vs_label.py \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_snrperband_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band" \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_snrperband_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band" \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_10label.json" --dataset-label "LRS -- SNR/A defined at 6000\AA" \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_10label.json" --dataset-label "HRS -- SNR/A defined at 6000\AA" \
#  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_apokasc_snrperband"

#python2.7 mean_performance_vs_label.py \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_snrperband_noblue_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band (no blue)" \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_snrperband_noblue_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band (no blue)" \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_snrperband_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band" \
#  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_snrperband_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band" \
#  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_apokasc_snrperband_noblue"

for mode in lrs hrs
do

python2.7 mean_performance_vs_label.py \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>-1" --dataset-label "Giants; [Fe/H]$>-1$" --dataset-colour "blue" --dataset-linetype 1 \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>-1" --dataset-label "Dwarfs; [Fe/H]$>-1$" --dataset-colour "red" --dataset-linetype 1 \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored_${mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]<-1" --dataset-label "Giants; [Fe/H]$<-1$" --dataset-colour "green" --dataset-linetype 1 \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored_${mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]<-1" --dataset-label "Dwarfs; [Fe/H]$<-1$" --dataset-colour "orange" --dataset-linetype 1 \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparisonA_ahm2017_${mode}"

python2.7 mean_performance_vs_label.py \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored_${mode}_3label.json" --dataset-label "3 parameter; censored" --dataset-colour "blue" --dataset-linetype 1 \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_censored_${mode}_10label.json" --dataset-label "10 parameters; censored" --dataset-colour "red" --dataset-linetype 1 \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_${mode}_3label.json" --dataset-label "3 parameter; uncensored" --dataset-colour "green" --dataset-linetype 1 \
  --cannon-output "../../output_data/cannon/cannon_ahm2017_perturbed_${mode}_10label.json" --dataset-label "10 parameters; uncensored" --dataset-colour "orange" --dataset-linetype 1 \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparisonB_ahm2017_${mode}"

done

for cannon_output in ../../output_data/cannon/*.json
do

cannon_run=`echo ${cannon_output} | sed 's@../../output_data/cannon/\(.*\).json@\1@g'`

python2.7 mean_performance_vs_label.py --cannon-output "${cannon_output}" \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/${cannon_run}"

python2.7 scatter_plot_cannon_uncertainty.py --cannon-output "${cannon_output}" \
  --output-stub "../../output_plots/cannon_performance/uncertainties/${cannon_run}"

for colour_label in "Teff" "logg" "[Fe/H]" "[Ca/H]" "[Mg/H]" "[Ti/H]" "[Si/H]" "[Na/H]" "[Ni/H]" "[Cr/H]"
do

target_accuracy="0.1"
if [ "$colour_label" == "Teff" ] ; then target_accuracy="100" ; fi
if [ "$colour_label" == "logg" ] ; then target_accuracy="0.3" ; fi

accuracy_unit="dex"
if [ "$colour_label" == "Teff" ] ; then accuracy_unit="K" ; fi

path_safe_label=`echo ${colour_label} | sed -e 's@\[\(.*\)/H\]@\1H@g'`

python2.7 scatter_plot_snr_required.py --label "Teff{7000:3400}" --label "logg{5:0}" \
  --label-axis-latex "Teff" --label-axis-latex "log(g)" \
  --label-axis-latex "${colour_label}" \
  --colour-by-label "${colour_label}" \
  --target-accuracy "${target_accuracy}" \
  --colour-range-min 30 --colour-range-max 120 \
  --cannon-output "${cannon_output}" \
  --accuracy-unit "${accuracy_unit}" \
  --output-stub "../../output_plots/cannon_performance/required_snrA/${cannon_run}_${path_safe_label}"

python2.7 scatter_plot_snr_required.py --label "[Fe/H]{1:-3}" --label "logg{5:0}" \
  --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
  --label-axis-latex "${colour_label}" \
  --colour-by-label "${colour_label}" \
  --target-accuracy "${target_accuracy}" \
  --colour-range-min 30 --colour-range-max 120 \
  --cannon-output "${cannon_output}" \
  --accuracy-unit "${accuracy_unit}" \
  --output-stub "../../output_plots/cannon_performance/required_snrB/${cannon_run}_${path_safe_label}"

python2.7 scatter_plot_coloured.py --label "Teff{7000:3400}" --label "logg{5:0}" \
  --label-axis-latex "Teff" --label-axis-latex "log(g)" \
  --label-axis-latex "${colour_label}" \
  --colour-by-label "${colour_label}{:}" \
  --colour-range-min " -$(python2.7 -c "print ${target_accuracy}*3")" \
  --colour-range-max " $(python2.7 -c "print ${target_accuracy}*3")" \
  --cannon-output "${cannon_output}" \
  --output-stub "../../output_plots/cannon_performance/label_offsets/A_${cannon_run}_${path_safe_label}"

python2.7 scatter_plot_coloured.py --label "[Fe/H]{1:-3}" --label "logg{5:0}" \
  --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
  --label-axis-latex "${colour_label}" \
  --colour-by-label "${colour_label}{:}" \
  --colour-range-min " -$(python2.7 -c "print ${target_accuracy}*3")" \
  --colour-range-max " $(python2.7 -c "print ${target_accuracy}*3")" \
  --cannon-output "${cannon_output}" \
  --output-stub "../../output_plots/cannon_performance/label_offsets/B_${cannon_run}_${path_safe_label}"

done
done
