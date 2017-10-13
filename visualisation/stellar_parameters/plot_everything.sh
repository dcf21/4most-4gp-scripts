#!/usr/bin/env bash

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots/stellar_parameters

# -------------------------------------------------------------------------------------------------------------------

python scatter_plot.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                       --label "[Fe/H]{-1:0.6}" --label "[Mg/H]{-0.4:1.2}" \
                       --label-axis-latex "[Fe/H]" --label-axis-latex "[Mg/Fe]" \
                       --using "\$1:(\$2-\$1)" \
                       --output ../../output_plots/stellar_parameters/apogee_magnesium_test

python scatter_plot.py --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                       --label "[Fe/H]{-1:0.6}" --label "[Mg/H]{-0.4:1.2}" \
                       --label-axis-latex "[Fe/H]" --label-axis-latex "[Mg/Fe]" \
                       --using "\$1:(\$2-\$1)" \
                       --output ../../output_plots/stellar_parameters/apogee_magnesium_training

python scatter_plot.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                       --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                       --output ../../output_plots/stellar_parameters/apogee_teff_logg_both

python scatter_plot.py --library turbospec_apokasc_test_set --library-colour red --library-title "Test set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                       --output ../../output_plots/stellar_parameters/apogee_teff_logg_test

python scatter_plot.py --library turbospec_apokasc_training_set --library-colour blue --library-title "Training set" \
                       --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
                       --label-axis-latex "Teff" --label-axis-latex "log(g)" \
                       --output ../../output_plots/stellar_parameters/apogee_teff_logg_training

# -------------------------------------------------------------------------------------------------------------------

for library_path in ../../workspace/turbospec_*
do

library="$(basename "${library_path}")"

python scatter_plot_coloured.py --library ${library} \
                                --label "Teff{7000:3400}" --label "logg{5:0}" --label "[Fe/H]{:}" \
                                --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                                --colour-range-min 0.5 --colour-range-max -0.7 \
                                --output ../../output_plots/stellar_parameters/hr_coloured_${library}

python histogram.py --library ${library} \
                    --label "Teff{7000:3400}" --label "logg{5:0}" --label "[Fe/H]{1:-3}" \
                    --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
                    --using "\$1" --using "\$2" --using "\$3" \
                    --output ../../output_plots/stellar_parameters/histogram_${library}

done