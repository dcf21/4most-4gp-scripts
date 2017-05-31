#!/bin/bash

# Activate python virtual environment
source ../virtualenv/bin/activate

# Make sure we've got the latest version of the 4GP libraries installed in virtual environment
cd ../4most-4gp/src/pythonModules/fourgp_speclib
python setup.py install
cd ../fourgp_cannon
python setup.py install
cd ../fourgp_rv
python setup.py install

# Do unit testing
cd ../fourgp_speclib/fourgp_speclib/tests
python -m unittest discover -v

# Wipe our temporary workspace
cd ../../../../../../4most-4gp-scripts
mkdir -p workspace
rm -Rf workspace/*

# Import test spectra
cd import_grids/
python import_brani_grid.py
python import_apokasc.py

# Test RV determination
cd ../test_rv_determination
python rv_test.py

# Test Cannon
cd ../test_cannon_degraded_spec/

python cannon_test.py --train APOKASC_trainingset_HRS --test testset_HRS \
                      --output_file /tmp/cannon_test_hrs

python cannon_test.py --train APOKASC_trainingset_HRS --test testset_HRS \
                      --censor ../../4MOST_testspectra/ges_master_v5.fits \
                      --output_file /tmp/cannon_test_hrs_censored

python cannon_test.py --train APOKASC_trainingset_LRS --test testset_HRS \
                      --output_file /tmp/cannon_test_lrs

python cannon_test.py --train APOKASC_trainingset_LRS --test testset_HRS \
                      --censor ../../4MOST_testspectra/ges_master_v5.fits \
                      --output_file /tmp/cannon_test_lrs_censored

