#!/bin/bash

# This script updates the local installation of 4GP

cwd=`pwd`

# Activate python virtual environment
source ../virtualenv/bin/activate

# Delete old package versions, just to be sure
pip uninstall -y fourgp_speclib
pip uninstall -y fourgp_cannon
pip uninstall -y fourgp_degrade
pip uninstall -y fourgp_rv
pip uninstall -y fourgp_specsynth
pip uninstall -y fourgp_telescope_data
pip uninstall -y fourgp_fourfs


# Make sure we've got the latest version of the 4GP libraries installed in virtual environment
cd ${cwd}
cd ../4most-4gp/src/pythonModules/fourgp_speclib
python2.7 setup.py clean --all  # No. Really. I don't want you to cache an old version of my code.
python2.7 setup.py install --force  # How many times do I need to tell you not to cache my code?
cd ../fourgp_cannon
python2.7 setup.py clean --all
python2.7 setup.py install --force
cd ../fourgp_degrade
python2.7 setup.py clean --all
python2.7 setup.py install --force
cd ../fourgp_rv
python2.7 setup.py clean --all
python2.7 setup.py install --force
cd ../fourgp_specsynth
python2.7 setup.py clean --all
python2.7 setup.py install --force
cd ../fourgp_telescope_data
python2.7 setup.py clean --all
python2.7 setup.py install --force
cd ../fourgp_fourfs
python2.7 setup.py clean --all
python2.7 setup.py install --force

