#!/bin/bash

# Activate python virtual environment
source ../virtualenv/bin/activate

python degrade_library_with_4fs.py --input-library demo_stars \
                                   --output-library-lrs 4fs_demo_stars_lrs \
                                   --output-library-hrs 4fs_demo_stars_hrs

python degrade_library_with_4fs.py --input-library turbospec_marcs_grid \
                                   --output-library-lrs 4fs_marcs_grid_lrs \
                                   --output-library-hrs 4fs_marcs_grid_hrs

python degrade_library_with_4fs.py --input-library turbospec_ahm2017_perturbed \
                                   --output-library-lrs 4fs_ahm2017_perturbed_lrs \
                                   --output-library-hrs 4fs_ahm2017_perturbed_hrs

python degrade_library_with_4fs.py --input-library turbospec_ges_dwarfs_perturbed \
                                   --output-library-lrs 4fs_ges_dwarfs_perturbed_lrs \
                                   --output-library-hrs 4fs_ges_dwarfs_perturbed_hrs

