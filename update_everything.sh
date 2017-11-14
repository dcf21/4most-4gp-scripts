#!/bin/bash

# This script updates the local installation of 4GP

cwd=`pwd`

# Activate python virtual environment
source ../virtualenv/bin/activate

# Make sure we've got the latest version of the 4GP libraries installed in virtual environment
cd ${cwd}
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

