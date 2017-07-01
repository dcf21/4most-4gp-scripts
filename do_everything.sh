#!/bin/bash

# This script runs all of the various scripts in this git repository.

# It is provided for two reasons: firstly it demonstrates the correct command-line syntax for running each script.
# Secondly, it is useful as a test. If all the scripts below complete without error, then everything is working.

# Activate python virtual environment
source ../virtualenv/bin/activate

# Make sure we've got the latest version of the 4GP libraries installed in virtual environment
cd ../4most-4gp/src/pythonModules/fourgp_speclib
python setup.py install
cd ../fourgp_cannon
python setup.py install
cd ../fourgp_degrade
python setup.py install
cd ../fourgp_rv
python setup.py install
cd ../fourgp_specsynth
python setup.py install
cd ../fourgp_telescope_data
python setup.py install
cd ../fourgp_fourfs
python setup.py install

# Do unit testing
cd ../fourgp_speclib/fourgp_speclib/tests
python -m unittest discover -v

# Wipe our temporary workspace
cd ../../../../../../4most-4gp-scripts
mkdir -p workspace
rm -Rf workspace/*

# Import test spectra
# cd import_grids/
# python import_brani_grid.py
# python import_apokasc.py

# Synthesize test spectra
cd ../synthesize_grids/
python synthesize_apokasc.py --output_library APOKASC_trainingset_turbospec \
                             --star_list ../../4MOST_testspectra/trainingset_param.tab \
                             --limit 5

python synthesize_apokasc.py --output_library APOKASC_testset_turbospec \
                             --star_list ../../4MOST_testspectra/testset_param.tab \
                             --limit 5

# Test RV determination
# cd ../test_rv_determination
# python rv_test.py &> /tmp/rv_test_out.txt

# Test Cannon
# cd ../test_cannon_degraded_spec/
# 
# python cannon_test.py --train APOKASC_trainingset_HRS --test testset_HRS \
#                       --output_file /tmp/cannon_test_hrs
# 
# python cannon_test.py --train APOKASC_trainingset_HRS --test testset_HRS \
#                       --censor ../../4MOST_testspectra/ges_master_v5.fits \
#                       --output_file /tmp/cannon_test_hrs_censored
# 
# python cannon_test.py --train APOKASC_trainingset_LRS --test testset_LRS \
#                       --output_file /tmp/cannon_test_lrs
# 
# python cannon_test.py --train APOKASC_trainingset_LRS --test testset_LRS \
#                       --censor ../../4MOST_testspectra/ges_master_v5.fits \
#                       --output_file /tmp/cannon_test_lrs_censored

