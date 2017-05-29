#!/bin/bash

# Activate python virtual environment
source ../virtualenv/bin/activate

# Make sure we've got the latest version of the 4GP libraries installed in virtual environment
cd ../4most-4gp/src/pythonModules/fourgp_speclib
python setup.py install
cd ../fourgp_cannon
python setup.py install

# Wipe our temporary workspace
cd ../../../../4most-4gp-scripts
mkdir -p workspace
rm -Rf workspace/*

# Import test spectra
cd import_grids/
python import_brani_grid.py
python import_apokasc.py

# Test Cannon
cd ../test_cannon_degraded_spec/
python cannon_test.py HRS none /tmp

