#!/bin/bash

# This script is designed to be run on aurora.lunarc.lu.se
# It installs the Cannon and 4GP in Dominic's home directory

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

cd /home/dominic/iwg7_pipeline

cd AnniesLasso
pip install --upgrade .

cd ../4most-4gp/src/pythonModules/fourgp_speclib/
pip install --upgrade .
cd ../fourgp_cannon
pip install --upgrade .
cd ../fourgp_degrade
pip install --upgrade .
# This depends on emcee, which isn't installed...
# cd ../fourgp_rv
# pip install --upgrade .
cd ../fourgp_specsynth
pip install --upgrade .
cd ../fourgp_telescope_data
pip install --upgrade .
cd ../fourgp_fourfs
pip install --upgrade .

