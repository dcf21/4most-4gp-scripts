#!/bin/bash

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots/cannon_performance/arrows
mkdir -p ../../output_plots/cannon_performance/performance_vs_snr
mkdir -p ../../output_plots/cannon_performance/uncertainties
mkdir -p ../../output_plots/cannon_performance/required_snrA
mkdir -p ../../output_plots/cannon_performance/required_snrB
mkdir -p ../../output_plots/cannon_performance/label_offsets

python scatter_plot_arrows.py --output-stub "../../output_plots/cannon_performance/arrows/apokasc_teff_logg_hrs_offset_arrows" \
                              --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                              --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                              --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_10label.json"

python scatter_plot_arrows.py --output-stub "../../output_plots/cannon_performance/arrows/apokasc_teff_logg_lrs_offset_arrows" \
                              --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                              --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                              --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_10label.json"

python mean_performance_vs_snr.py \
  --cannon-output "../../output_data/cannon/cannon_hawkins_lrs_10label.json" --dataset-label "Hawkins LRS" \
  --cannon-output "../../output_data/cannon/cannon_hawkins_hrs_10label.json" --dataset-label "Hawkins HRS" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_10label.json" --dataset-label "Ford LRS" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_10label.json" --dataset-label "Ford HRS" \
  --output-file "../../output_plots/cannon_performance/performance_vs_snr/apokasc_hawkins_comparison"

python mean_performance_vs_snr.py \
  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_snrperband_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_snrperband_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_10label.json" --dataset-label "LRS -- SNR/A defined at 6000\AA" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_10label.json" --dataset-label "HRS -- SNR/A defined at 6000\AA" \
  --output-file "../../output_plots/cannon_performance/performance_vs_snr/apokasc_snrperband_comparison"

python mean_performance_vs_snr.py \
  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_snrperband_noblue_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band (no blue)" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_snrperband_noblue_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band (no blue)" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_lrs_snrperband_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band" \
  --cannon-output "../../output_data/cannon/cannon_apokasc_hrs_snrperband_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band" \
  --output-file "../../output_plots/cannon_performance/performance_vs_snr/apokasc_snrperband_noblue_comparison"

for cannon_output in ../../output_data/cannon/*.json
do

cannon_run=`echo ${cannon_output} | sed 's@../../output_data/cannon/\(.*\).json@\1@g'`

python mean_performance_vs_snr.py --cannon-output "${cannon_output}" \
                                  --output-file "../../output_plots/cannon_performance/performance_vs_snr/${cannon_run}"

python scatter_plot_cannon_uncertainty.py --cannon-output "${cannon_output}" \
                                          --output-stub "../../output_plots/cannon_performance/uncertainties/${cannon_run}"

for colour_label in "Teff" "logg" "[Fe/H]"
do

target_accuracy="0.1"
if [ "$colour_label" == "Teff" ] ; then target_accuracy="100" ; fi
if [ "$colour_label" == "logg" ] ; then target_accuracy="0.3" ; fi

accuracy_unit="dex"
if [ "$colour_label" == "Teff" ] ; then accuracy_unit="K" ; fi

path_safe_label=`echo ${colour_label} | sed -e 's@\[\(.*\)/H\]@\1H@g'`

python scatter_plot_snr_required.py --label "Teff{7000:3400}" --label "logg{5:0}" \
                                    --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                                    --label-axis-latex "${colour_label}" \
                                    --colour-by-label "${colour_label}" \
                                    --target-accuracy "${target_accuracy}" \
                                    --colour-range-min 30 --colour-range-max 120 \
                                    --cannon-output "${cannon_output}" \
                                    --accuracy-unit "${accuracy_unit}" \
                                    --output-stub "../../output_plots/cannon_performance/required_snrA/${cannon_run}_${path_safe_label}"

python scatter_plot_snr_required.py --label "[Fe/H]{1:-3}" --label "logg{5:0}" \
                                    --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
                                    --label-axis-latex "${colour_label}" \
                                    --colour-by-label "${colour_label}" \
                                    --target-accuracy "${target_accuracy}" \
                                    --colour-range-min 30 --colour-range-max 120 \
                                    --cannon-output "${cannon_output}" \
                                    --accuracy-unit "${accuracy_unit}" \
                                    --output-stub "../../output_plots/cannon_performance/required_snrB/${cannon_run}_${path_safe_label}"

python scatter_plot_coloured.py --label "Teff{7000:3400}" --label "logg{5:0}" \
                                --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                                --label-axis-latex "${colour_label}" \
                                --colour-by-label "${colour_label}{:}" \
                                --colour-range-min " -$(python -c "print ${target_accuracy}*3")" \
                                --colour-range-max " $(python -c "print ${target_accuracy}*3")" \
                                --cannon-output "${cannon_output}" \
                                --output-stub "../../output_plots/cannon_performance/label_offsets/A_${cannon_run}_${path_safe_label}"

python scatter_plot_coloured.py --label "[Fe/H]{1:-3}" --label "logg{5:0}" \
                                --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
                                --label-axis-latex "${colour_label}" \
                                --colour-by-label "${colour_label}{:}" \
                                --colour-range-min " -$(python -c "print ${target_accuracy}*3")" \
                                --colour-range-max " $(python -c "print ${target_accuracy}*3")" \
                                --cannon-output "${cannon_output}" \
                                --output-stub "../../output_plots/cannon_performance/label_offsets/B_${cannon_run}_${path_safe_label}"

done
done

