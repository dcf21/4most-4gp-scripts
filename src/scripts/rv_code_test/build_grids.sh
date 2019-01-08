#!/bin/bash

# Create grids of template spectra for use with cross-correlation code. Also create a library of test spectra, merging the GALAH sample with some additional hot stars.

# Make a rectangular grid of synthetic spectra for T<8000K
../synthesize_samples/synthesize_rv_fitting_grid.py

# Import Joachim Bestenlehner's hot star templates and test objects
./import_hot_stars.py

# Merge two grids of templates
../rearrange_libraries/rearrange.py --create --input-library "hot_star_templates" --output-library rv_templates
../rearrange_libraries/rearrange.py --no-create --input-library turbospec_rv_templates --output-library rv_templates

# Resample cross-correlation templates
./resample_cross_correlation_grid.py --templates-in rv_templates --templates-out rv_templates_resampled

# Create test sample
../rearrange_libraries/rearrange.py --create --input-library galah_test_sample_turbospec --output-library rv_test_objects
../rearrange_libraries/rearrange.py --no-create --input-library hot_star_test_objects --output-library rv_test_objects

