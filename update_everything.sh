#!/bin/bash

# This script updates the local installation of 4GP

# Below we do a bit of brute-force uninstallation and cleaning of the python environment, as otherwise we can
# end up reinstalling a cached old version of packages, rather than forcing a download of a new copy of a package

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

# Install some of the python packages we required
pip install numpy scipy astropy mysqlclient flask matplotlib tables

# These additional packages are required by Sergey's RV code
pip install pyyaml numdifftools pandas

# Make sure we've got the latest version of the 4GP libraries installed in virtual environment
cd ${cwd}
cd ../4most-4gp/src/pythonModules/fourgp_speclib
python3 setup.py clean --all  # No. Really. I don't want you to cache an old version of my code.
python3 setup.py install --force  # How many times do I need to tell you not to cache my code?
cd ../fourgp_cannon
python3 setup.py clean --all
python3 setup.py install --force
cd ../fourgp_degrade
python3 setup.py clean --all
python3 setup.py install --force
cd ../fourgp_rv
python3 setup.py clean --all
python3 setup.py install --force
cd ../fourgp_specsynth
python3 setup.py clean --all
python3 setup.py install --force
cd ../fourgp_telescope_data
python3 setup.py clean --all
python3 setup.py install --force
cd ../fourgp_fourfs
python3 setup.py clean --all
python3 setup.py install --force

# Make sure we've got the latest version of the Cannon installed in virtual environment
cd ${cwd}
cd ../AnniesLasso
python3 setup.py clean --all
python3 setup.py install --force

# Make sure we've got the latest version of pyphot installed in virtual environment
cd ${cwd}
cd ../pyphot
python3 setup.py clean --all
python3 setup.py install --force

# Make sure we've got the latest version of Sergey's RV code installed in virtual environment
cd ${cwd}
cd ../rvspecfit
python3 setup.py clean --all
python3 setup.py install --force
