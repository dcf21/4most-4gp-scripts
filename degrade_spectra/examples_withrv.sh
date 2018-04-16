#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

# Add radial velocities to GALAH test stars
python2.7 degrade_library_with_rv.py --input-library galah_test_sample_turbospec \
                                     --output-library  galah_test_sample_withrv \
                                     --db-in-tmp

python2.7 degrade_library_with_4fs.py --input-library galah_test_sample_withrv \
                                      --snr-list 50 \
                                      --mag-list 15 \
                                      --photometric-band "GROUND_JOHNSON_V" \
                                      --output-library-lrs galah_test_sample_withrv_4fs_snr50_lrs \
                                      --output-library-hrs galah_test_sample_withrv_4fs_snr50_hrs