#!/bin/bash

source ../../../virtualenv/bin/activate

python scatter_plot_arrows.py --library 4fs_apokasc_test_set_hrs \
                              --output-stub ../../output_plots/apogee_teff_logg_hrs_offset_arrows \
                              --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                              --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                              --cannon_output ../../output_data/cannon_test_4fs_hrs.dat

python scatter_plot_arrows.py --library 4fs_apokasc_test_set_lrs \
                              --output-stub ../../output_plots/apogee_teff_logg_lrs_offset_arrows \
                              --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                              --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                              --cannon_output ../../output_data/cannon_test_4fs_lrs.dat

python mean_performance_vs_snr.py \
  --library hawkins_apokasc_test_set_lrs --cannon-output ../../output_data/cannon_test_hawkins_lrs.dat --dataset-label "Hawkins LRS" \
  --library hawkins_apokasc_test_set_hrs --cannon-output ../../output_data/cannon_test_hawkins_hrs.dat --dataset-label "Hawkins HRS" \
  --library 4fs_apokasc_test_set_lrs --cannon-output ../../output_data/cannon_test_4fs_lrs.dat --dataset-label "Ford LRS" \
  --library 4fs_apokasc_test_set_hrs --cannon-output ../../output_data/cannon_test_4fs_hrs.dat --dataset-label "Ford HRS" \
  --output-file ../../output_plots/apogee_mean_performance

python scatter_plot_coloured.py --library 4fs_apokasc_test_set_lrs \
                                --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                                --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "Error in Teff" \
                                --colour-by-label "Teff{:}" \
                                --colour-range-min -400 --colour-range-max 400 \
                                --cannon_output ../../output_data/cannon_test_4fs_lrs.dat \
                                --output-stub ../../output_plots/apogee_Teff_performance_hr
