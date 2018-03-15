#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python2.7 degrade_library_with_4fs.py --input-library turbospec_demo_stars \
                                      --output-library-lrs 4fs_demo_stars_lrs \
                                      --output-library-hrs 4fs_demo_stars_hrs

for all in ../workspace/turbospec_*
do

run_name=$(echo ${all} | sed 's@../workspace/turbospec_\(.*\)@\1@g')

python2.7 degrade_library_with_4fs.py --input-library turbospec_${run_name} \
                                      --output-library-lrs 4fs_${run_name}_lrs \
                                      --output-library-hrs 4fs_${run_name}_hrs

done

