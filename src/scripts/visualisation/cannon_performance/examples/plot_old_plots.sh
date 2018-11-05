#!/bin/bash

# This is the graveyard where we put ancient plots

# ---

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../../virtualenv/bin/activate

# ---

# Create directories where plots get held
mkdir -p ../../../../output_plots/cannon_performance/arrows
mkdir -p ../../../../output_plots/cannon_performance/performance_vs_label
mkdir -p ../../../../output_plots/cannon_performance/uncertainties
mkdir -p ../../../../output_plots/cannon_performance/required_snrA
mkdir -p ../../../../output_plots/cannon_performance/required_snrB
mkdir -p ../../../../output_plots/cannon_performance/label_offsets

# Produce an HR diagram with arrows showing the difference between the input and output stellar parameters for the APOGEE giants
for mode in lrs hrs
do
    python3 scatter_plot_arrows.py --output-stub "../../../../output_plots/cannon_performance/arrows/apokasc_teff_logg_${mode}_offset_arrows" \
      --label "Teff{5100:4000}" --label "logg{3.8:1.2}" \
      --label-axis-latex "Teff" --label-axis-latex "log(g)" \
      --cannon-output "../../../../output_data/cannon/cannon_apokasc_${mode}_10label.json"
done

# comparison_apokasc_hawkins
# Produce performance vs SNR plots for the APOGEE giants, using Hawkins spectrum library vs Ford spectrum library
python3 mean_performance_vs_label.py \
  --cannon-output "../../../../output_data/cannon/cannon_hawkins_lrs_10label.json" --dataset-label "Hawkins LRS" \
  --cannon-output "../../../../output_data/cannon/cannon_hawkins_hrs_10label.json" --dataset-label "Hawkins HRS" \
  --cannon-output "../../../../output_data/cannon/cannon_apokasc_lrs_10label.json" --dataset-label "Ford LRS" \
  --cannon-output "../../../../output_data/cannon/cannon_apokasc_hrs_10label.json" --dataset-label "Ford HRS" \
  --output-file "../../../../output_plots/cannon_performance/performance_vs_label/comparison_apokasc_hawkins"

# comparison_apokasc_snrperband
# Bonkers tests where we defined the SNR in each wavelength arm separately
#python3 mean_performance_vs_label.py \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_lrs_snrperband_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band" \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_hrs_snrperband_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band" \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_lrs_10label.json" --dataset-label "LRS -- SNR/A defined at 6000\AA" \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_hrs_10label.json" --dataset-label "HRS -- SNR/A defined at 6000\AA" \
#  --output-file "../../../../output_plots/cannon_performance/performance_vs_label/comparison_apokasc_snrperband"

# Bonkers tests where we disabled the blue-most wavelength arms of 4MOST entirely
#python3 mean_performance_vs_label.py \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_lrs_snrperband_noblue_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band (no blue)" \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_hrs_snrperband_noblue_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band (no blue)" \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_lrs_snrperband_10label.json" --dataset-label "LRS -- SNR/A defined in centre of each band" \
#  --cannon-output "../../../../output_data/cannon/cannon_apokasc_hrs_snrperband_10label.json" --dataset-label "HRS -- SNR/A defined in centre of each band" \
#  --output-file "../../../../output_plots/cannon_performance/performance_vs_label/comparison_apokasc_snrperband_noblue"
