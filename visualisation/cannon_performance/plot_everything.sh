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

python scatter_plot_snr_required.py --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                                    --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "Teff" \
                                    --colour-by-label "Teff{:}" \
                                    --target-accuracy 100 \
                                    --colour-range-min 80 --colour-range-max 180 \
                                    --cannon_output ../../output_data/cannon_apokasc_lrs.json \
                                    --output-stub ../../output_plots/apokasc_Teff_required_snr

