#!/bin/bash

# This script is designed to be run on aurora.lunarc.lu.se
# It installs the Cannon and 4GP in Dominic's home directory

module load GCC/5.4.0-2.26  OpenMPI/1.10.3  scipy/0.17.0-Python-2.7.11  SQLite/3.20.1  SQLite/3.9.2
export PYTHONPATH=$HOME/local/lib/python2.7/site-packages:${PYTHONPATH}

cd /home/dominic/iwg7_pipeline

cd AnniesLasso
python2.7 setup.py install --prefix=$HOME/local

cd ../4most-4gp/src/pythonModules/fourgp_speclib/
python2.7 setup.py install --prefix=$HOME/local
cd ../fourgp_cannon
python2.7 setup.py install --prefix=$HOME/local
cd ../fourgp_degrade
python2.7 setup.py install --prefix=$HOME/local
cd ../fourgp_rv
python2.7 setup.py install --prefix=$HOME/local
cd ../fourgp_specsynth
python2.7 setup.py install --prefix=$HOME/local
cd ../fourgp_telescope_data
python2.7 setup.py install --prefix=$HOME/local
cd ../fourgp_fourfs
python2.7 setup.py install --prefix=$HOME/local

