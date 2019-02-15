#!/bin/bash

# This script is designed to be run on aurora.lunarc.lu.se

# It installs the Cannon and 4GP in a conda python environment in Dominic's home directory

# The first time you install 4GP on lunarc, you need to first create your own virtual environment
# via the commands:

# module add Anaconda3
# conda create --name myenv
# conda install scipy

# The commands below switch to a pre-existing Anaconda environment, and make sure we have
# the latest versions of all the 4GP packages and their dependencies.

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda3

# This line used to work up until Feb 2019...
source activate myenv

# ... but since it's stopped working, this line makes sure we use the right python ...
export PATH="/home/dominic/.conda/envs/myenv/bin:$PATH"

cd /home/dominic/iwg7_pipeline

cd AnniesLasso
python3 setup.py install

cd ../TheCannon
python3 setup.py install

cd ../../pyphot
python3 setup.py install

exit

cd ../4most-4gp/src/pythonModules/fourgp_speclib/
python3 setup.py develop

cd ../fourgp_cannon
python3 setup.py develop

cd ../fourgp_payne
python3 setup.py develop

cd ../fourgp_degrade
python3 setup.py develop

# cd ../fourgp_rv
# python3 setup.py develop

cd ../fourgp_specsynth
python3 setup.py develop

cd ../fourgp_telescope_data
python3 setup.py develop

cd ../fourgp_fourfs
python3 setup.py develop

cd ../fourgp_pipeline
python3 setup.py develop

