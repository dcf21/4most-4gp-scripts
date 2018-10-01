#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work

# Add radial velocities to GALAH test stars
python3 degrade_library_with_rv.py --input-library galah_test_sample_turbospec \
                                   --output-library  galah_test_sample_withrv \
                                   --db-in-tmp

python3 degrade_library_with_4fs.py --input-library galah_test_sample_withrv \
                                    --snr-list 50 \
                                    --mag-list 15 \
                                    --photometric-band "GROUND_JOHNSON_V" \
                                    --output-library-lrs galah_test_sample_withrv_4fs_snr50_lrs \
                                    --output-library-hrs galah_test_sample_withrv_4fs_snr50_hrs

