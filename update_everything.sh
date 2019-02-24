#!/bin/bash

# This script updates the local installation of 4GP in a python virtual environment

# Make absolutely sure we're in the right directory to start with
cd "$(dirname "$0")"
cwd=`pwd`

# Sometimes this line is necessary, if your locale settings are broken
export LC_ALL=C

# Below we do a bit of brute-force uninstallation and cleaning of the python environment, as otherwise we can
# end up reinstalling a cached old version of packages, rather than forcing a download of a new copy of a package

rm -Rf ../virtualenv
virtualenv -p python3 ../virtualenv

# Activate python virtual environment
source ../virtualenv/bin/activate

# Install some of the python packages we required
pip install numpy==1.15.3  # Currently, 1.16.0 doesn't actually install
pip install scipy astropy mysqlclient flask matplotlib tables

# These additional packages are required by Sergey's RV code
pip install pyyaml numdifftools pandas

# Make sure we've got the latest version of the 4GP libraries installed in virtual environment
cd ${cwd}

cd ../4most-4gp/src/pythonModules/fourgp_speclib
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_cannon
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_payne
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_degrade
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_rv
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_specsynth
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_telescope_data
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_fourfs
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

cd ../fourgp_pipeline
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py develop

# Make sure we've got the old version of Andy Casey's Cannon installed in virtual environment
cd ${cwd}
cd ../AnniesLasso
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py install

# Make sure we've got the latest version of Anno Ho's Cannon installed in virtual environment
# cd ${cwd}
# cd ../TheCannon
# rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
# python3 setup.py install

# Make sure we've got the latest version of pyphot installed in virtual environment
cd ${cwd}
cd ../pyphot
rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
python3 setup.py install

# Make sure we've got the latest version of Sergey's RV code installed in virtual environment
# cd ${cwd}
# cd ../rvspecfit
# rm -Rf build dist *.egg-info  # Clear out the cache to make sure we install latest version of code
# python3 setup.py install
