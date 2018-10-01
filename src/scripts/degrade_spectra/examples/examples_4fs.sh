#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
python3 degrade_library_with_4fs.py --input-library demo_stars \
                                    --output-library-lrs 4fs_demo_stars_lrs \
                                    --output-library-hrs 4fs_demo_stars_hrs

python3 degrade_library_with_4fs.py --input-library galah_test_sample_turbospec \
                                    --snr-list "10,12,14,16,18,20,23,26,30,35,40,45,50,80,100,130,180,250" \
                                    --output-library-lrs galah_test_sample_4fs_lrs \
                                    --output-library-hrs galah_test_sample_4fs_hrs

python3 degrade_library_with_4fs.py --input-library galah_training_sample_turbospec \ 
                                    --snr-list "250" \
                                    --output-library-lrs galah_training_sample_4fs_lrs \
                                    --output-library-hrs galah_training_sample_4fs_hrs

# Examples for S4 only

python3 degrade_library_with_4fs.py --input-library galah_test_sample_turbospec \
                                    --snr-list "10,12,14,16,18,20,23,26,30,35,40,45,50,80,100,130,180,250" \
                                    --mag-list 15 \
                                    --photometric-band "GROUND_JOHNSON_V" \
                                    --snr-definitions-hrs "GalDiskHR_536NM" \
                                    --no-run-lrs \
                                    --output-library-hrs galah_test_sample_4fs_s4grn_hrs

python3 degrade_library_with_4fs.py --input-library galah_test_sample_turbospec \
                                    --snr-list "10,12,14,16,18,20,23,26,30,35,40,45,50,80,100,130,180,250" \
                                    --mag-list 15 \
                                    --photometric-band "GROUND_JOHNSON_V" \
                                    --snr-definitions-hrs "GalDiskHR_620NM" \
                                    --no-run-lrs \
                                    --output-library-hrs galah_test_sample_4fs_s4red_hrs

# A shell script to run all turbospec output through 4FS

#for all in ../../../workspace/turbospec_*
#do
#
#run_name=$(echo ${all} | sed 's@../../../workspace/turbospec_\(.*\)@\1@g')
#
#python3 degrade_library_with_4fs.py --input-library turbospec_${run_name} \
#                                    --output-library-lrs 4fs_${run_name}_lrs \
#                                    --output-library-hrs 4fs_${run_name}_hrs
#
#done

