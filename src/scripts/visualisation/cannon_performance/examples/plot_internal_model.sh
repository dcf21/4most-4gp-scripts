#!/bin/bash

# This script produces plots of the Cannon's internal model of how a region of
# the spectrum changes with [Fe/H]

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
mkdir -p ../../../../output_plots/cannon_performance/internal_model

# Produce a plot of the flux at a specific wavelength as a function of [Fe/H]
# Must use "rect_grid" spectrum library here, because we need multiple spectra at common Teff and log(g) while we vary
# [Fe/H]
python2.7 internal_model_one_wavelength.py \
    --output "../../../../output_plots/cannon_performance/internal_model/rect_grid_5731.7618" \
    --wavelength 5731.7618 \
    --label "[Fe/H]" \
    --label-axis-latex "[Fe/H]" \
    --fixed-label "Teff=6000" \
    --fixed-label "logg=4.2" \
    --cannon-output "../../../../output_data/cannon/cannon_rect_rect_lrs_3label"

# Produce a plot of the spectrum in the 5725 to 5735 A region, with curves at all available values of [Fe/H]
# Must use "rect_grid" spectrum library here, because we need multiple spectra at common Teff and log(g) while we vary
# [Fe/H]
python2.7 internal_model_span_wavelength.py \
    --output "../../../../output_plots/cannon_performance/internal_model/rect_grid_5725_5735" \
    --wavelength_min 5725 \
    --wavelength_max 5735 \
    --label "[Fe/H]" \
    --label-axis-latex "[Fe/H]" \
    --fixed-label "Teff=6000" \
    --fixed-label "logg=4.2" \
    --cannon-output "../../../../output_data/cannon/cannon_rect_rect_lrs_3label"
