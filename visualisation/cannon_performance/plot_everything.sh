#!/bin/bash

source ../../../virtualenv/bin/activate

python scatter_plot_arrows.py --output-stub ../../output_plots/apokasc_teff_logg_hrs_offset_arrows \
                              --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                              --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                              --cannon_output ../../output_data/cannon_apokasc_hrs.json

python scatter_plot_arrows.py --output-stub ../../output_plots/apokasc_teff_logg_lrs_offset_arrows \
                              --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                              --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                              --cannon_output ../../output_data/cannon_apokasc_lrs.json

python mean_performance_vs_snr.py \
  --cannon-output ../../output_data/cannon_hawkins_lrs.json --dataset-label "Hawkins LRS" \
  --cannon-output ../../output_data/cannon_hawkins_hrs.json --dataset-label "Hawkins HRS" \
  --cannon-output ../../output_data/cannon_apokasc_lrs.json --dataset-label "Ford LRS" \
  --cannon-output ../../output_data/cannon_apokasc_hrs.json --dataset-label "Ford HRS" \
  --output-file ../../output_plots/apokasc_mean_performance

python scatter_plot_coloured.py --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                                --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "Error in Teff" \
                                --colour-by-label "Teff{:}" \
                                --colour-range-min -400 --colour-range-max 400 \
                                --cannon_output ../../output_data/cannon_apokasc_lrs.json \
                                --output-stub ../../output_plots/apokasc_Teff_performance_hr

for colour_label in "Teff" "logg" "[Fe/H]"
do
for cannon_run in "apokasc_lrs" "apokasc_hrs" "ahm2017_perturbed_lrs" "ahm2017_perturbed_hrs" "ges_dwarfs_perturbed_lrs" "ges_dwarfs_perturbed_hrs" "marcs_ahm2017_lrs" "marcs_ahm2017_hrs"
do

target_accuracy=0.1
if [ "$colour_label" == "Teff" ] ; then target_accuracy=100 ; fi
if [ "$colour_label" == "logg" ] ; then target_accuracy=0.3 ; fi

path_safe_label=`echo ${colour_label} | sed -e 's@\[\(.*\)/H\]@\1H@g'`

title="Undefined"
if [ "$cannon_run" == "apokasc_lrs" ] ; then title="4MOST LRS - Train on APOKASC(1). Test on APOKASC(2)." ; fi
if [ "$cannon_run" == "apokasc_hrs" ] ; then title="4MOST HRS - Train on APOKASC(1). Test on APOKASC(2)." ; fi
if [ "$cannon_run" == "ahm2017_perturbed_lrs" ] ; then title="4MOST LRS - Train on GES UVES AHM2017. Test on perturbed version." ; fi
if [ "$cannon_run" == "ahm2017_perturbed_hrs" ] ; then title="4MOST HRS - Train on GES UVES AHM2017. Test on perturbed version." ; fi
if [ "$cannon_run" == "ges_dwarfs_perturbed_lrs" ] ; then title="4MOST LRS - Train on GES UVES dwarfs. Test on perturbed version." ; fi
if [ "$cannon_run" == "ges_dwarfs_perturbed_hrs" ] ; then title="4MOST HRS - Train on GES UVES dwarfs. Test on perturbed version." ; fi
if [ "$cannon_run" == "marcs_ahm2017_lrs" ] ; then title="4MOST LRS - Train on MARCS grid. Test on perturbed GES UVES AHM2017." ; fi
if [ "$cannon_run" == "marcs_ahm2017_hrs" ] ; then title="4MOST HRS - Train on MARCS grid. Test on perturbed GES UVES AHM2017." ; fi

python scatter_plot_snr_required.py --label "Teff{7000:3400}" --label "logg{5:0}" \
                                    --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                                    --label-axis-latex "${colour_label}" \
                                    --colour-by-label "${colour_label}" \
                                    --target-accuracy ${target_accuracy} \
                                    --colour-range-min 80 --colour-range-max 360 \
                                    --cannon_output ../../output_data/cannon_${cannon_run}.json \
                                    --title "${title}" \
                                    --output-stub "../../output_plots/required_snrA_${cannon_run}_${path_safe_label}"

python scatter_plot_snr_required.py --label "[Fe/H]{1:-3}" --label "logg{5:0}" \
                                    --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
                                    --label-axis-latex "${colour_label}" \
                                    --colour-by-label "${colour_label}" \
                                    --target-accuracy ${target_accuracy} \
                                    --colour-range-min 80 --colour-range-max 360 \
                                    --cannon_output ../../output_data/cannon_${cannon_run}.json \
                                    --title "${title}" \
                                    --output-stub "../../output_plots/required_snrB_${cannon_run}_${path_safe_label}"

done
done

