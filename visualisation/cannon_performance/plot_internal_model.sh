#!/bin/bash

source ../../../virtualenv/bin/activate

mkdir -p ../../output_plots/cannon_performance/internal_model

python internal_model_one_wavelength.py \
    --output-stub "../../output_plots/cannon_performance/internal_model/rect_grid_5731.7618" \
    --wavelength 5731.7618 \
    --label "[Fe/H]" \
    --label-axis-latex "[Fe/H]" \
    --fixed-label "Teff=6000" \
    --fixed-label "logg=4.2" \
    --library "4fs_rect_grid_lrs" \
    --train-library "4fs_rect_grid_lrs[SNR=250]" \
    --cannon-output "../../output_data/cannon/cannon_rect_rect_lrs_3label"

python internal_model_span_wavelength.py \
    --output-stub "../../output_plots/cannon_performance/internal_model/rect_grid_5725_5735" \
    --wavelength_min 5725 \
    --wavelength_max 5735 \
    --label "[Fe/H]" \
    --label-axis-latex "[Fe/H]" \
    --fixed-label "Teff=6000" \
    --fixed-label "logg=4.2" \
    --library "4fs_rect_grid_lrs[SNR=5000]" \
    --train-library "4fs_rect_grid_lrs[SNR=250]" \
    --cannon-output "../../output_data/cannon/cannon_rect_rect_lrs_3label"

