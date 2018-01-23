#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python2.7 redden_library.py --input-library demo_stars \
                            --output-library demo_stars_reddened \

python2.7 redden_library.py --input-library turbospec_ahm2017_perturbed \
                            --output-library reddened_ahm2017_perturbed \

python2.7 degrade_library_with_4fs.py --input-library reddened_ahm2017_perturbed \
                                      --snr-list 50 \
                                      --output-library-lrs 4fs_reddened_ahm2017_perturbed_lrs \
                                      --output-library-hrs 4fs_reddened_ahm2017_perturbed_hrs

