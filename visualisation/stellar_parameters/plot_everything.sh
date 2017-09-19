#!/usr/bin/env bash

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots

python scatter_plot.py --library 4fs_apokasc_test_set_hrs --library-colour red --library-title "Test set" \
                       --library 4fs_apokasc_training_set_hrs --library-colour blue --library-title "Training set" \
                       --label "[Fe/H]{-1:0.6}" --label "[Mg/H]{-0.4:1.2}" \
                       --label-axis-latex "[Fe/H]" --label-axis-latex "[Mg/Fe]" \
                       --using "\$1:(\$2-\$1)" \
                       --output ../../output_plots/apogee_magnesium

python scatter_plot.py --library 4fs_apokasc_test_set_hrs --library-colour red --library-title "Test set" \
                       --library 4fs_apokasc_training_set_hrs --library-colour blue --library-title "Training set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                       --output ../../output_plots/apogee_teff_logg

python scatter_plot_coloured.py \
                       --library 4fs_apokasc_test_set_hrs --library-title "Test set" \
                       --library 4fs_apokasc_training_set_hrs --library-title "Training set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" --label "[Fe/H]{:}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                       --colour-range-min 0.5 --colour-range-max -0.7 \
                       --output ../../output_plots/apogee_metallicity_hr

python scatter_plot_coloured.py \
                       --library 4fs_ahm2017_sample_hrs --library-title "Test set" \
                       --label "Teff{7000:3400}" --label "logg{5:0}" --label "[Fe/H]{:}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                       --colour-range-min 0.5 --colour-range-max -2 \
                       --output ../../output_plots/ges_metallicity_hr

python histogram.py --library 4fs_apokasc_test_set_hrs --library-colour red --library-title "Test set" \
                    --library 4fs_apokasc_training_set_hrs --library-colour blue --library-title "Training set" \
                    --label "[Fe/H]{-1:1}" \
                    --label-axis-latex "[Fe/H]" \
                    --using "\$1" \
                    --output ../../output_plots/apogee_metallicity_histogram