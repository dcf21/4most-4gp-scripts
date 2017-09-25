#!/usr/bin/env bash

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots

python scatter_plot.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                       --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                       --label "[Fe/H]{-1:0.6}" --label "[Mg/H]{-0.4:1.2}" \
                       --label-axis-latex "[Fe/H]" --label-axis-latex "[Mg/Fe]" \
                       --using "\$1:(\$2-\$1)" \
                       --output ../../output_plots/apogee_magnesium_combined

python scatter_plot.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                       --label "[Fe/H]{-1:0.6}" --label "[Mg/H]{-0.4:1.2}" \
                       --label-axis-latex "[Fe/H]" --label-axis-latex "[Mg/Fe]" \
                       --using "\$1:(\$2-\$1)" \
                       --output ../../output_plots/apogee_magnesium_test

python scatter_plot.py --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                       --label "[Fe/H]{-1:0.6}" --label "[Mg/H]{-0.4:1.2}" \
                       --label-axis-latex "[Fe/H]" --label-axis-latex "[Mg/Fe]" \
                       --using "\$1:(\$2-\$1)" \
                       --output ../../output_plots/apogee_magnesium_training

python scatter_plot.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                       --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                       --output ../../output_plots/apogee_teff_logg_both

python scatter_plot.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                       --output ../../output_plots/apogee_teff_logg_test

python scatter_plot.py --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                       --output ../../output_plots/apogee_teff_logg_training

python scatter_plot_coloured.py \
                       --library turbospec_apokasc_test_set --library-title "Test set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" --label "[Fe/H]{:}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                       --colour-range-min 0.5 --colour-range-max -0.7 \
                       --output ../../output_plots/apogee_metallicity_hr_test

python scatter_plot_coloured.py \
                       --library turbospec_apokasc_training_set --library-title "Training set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" --label "[Fe/H]{:}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                       --colour-range-min 0.5 --colour-range-max -0.7 \
                       --output ../../output_plots/apogee_metallicity_hr_training

python scatter_plot_coloured.py \
                       --library turbospec_ahm2017_sample --library-title "Test set" \
                       --label "Teff{7000:3400}" --label "logg{5:0}" --label "[Fe/H]{:}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                       --colour-range-min 0.5 --colour-range-max -2 \
                       --output ../../output_plots/ges_metallicity_hr

python scatter_plot_coloured.py \
                       --library turbospec_ges_dwarf_sample --library-title "Test set" \
                       --label "Teff{7000:3400}" --label "logg{5:0}" --label "[Fe/H]{:}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                       --colour-range-min 0.5 --colour-range-max -2 \
                       --output ../../output_plots/dwarfs_metallicity_hr

python scatter_plot_coloured.py \
                       --library turbospec_marcs_grid --library-title "Test set" \
                       --label "Teff{7000:3400}" --label "logg{5:0}" --label "[Fe/H]{:}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                       --colour-range-min 0.5 --colour-range-max -2 \
                       --output ../../output_plots/marcsgrid_metallicity_hr

python histogram.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                    --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                    --label "[Fe/H]{-1:1}" \
                    --label-axis-latex "[Fe/H]" \
                    --using "\$1" \
                    --output ../../output_plots/apogee_metallicity_histogram
