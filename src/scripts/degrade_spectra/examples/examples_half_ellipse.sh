#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
for mode in hrs lrs
do

python2.7 degrade_library_with_half_ellipse.py --input-library galah_training_sample_4fs_${mode} \
                                               --width 1.7 \
                                               --output-library galah_training_sample_4fs_he1.7_${mode} \
                                               --db-in-tmp

for he_width in 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.1 2.2
do

python2.7 degrade_library_with_half_ellipse.py --input-library galah_test_sample_4fs_${mode}_50only \
                                               --width ${he_width} \
                                               --output-library galah_test_sample_4fs_he${he_width}_${mode} \
                                               --db-in-tmp

done

done
