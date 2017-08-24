#!/bin/bash

# This script runs all of the various scripts in this git repository.

# It is provided for two reasons: firstly it demonstrates the correct command-line syntax for running each script.
# Secondly, it is useful as a test. If all the scripts below complete without error, then everything is working.

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

# Do unit testing
cd ${cwd}
cd ../4most-4gp/src/pythonModules/fourgp_speclib/fourgp_speclib/tests
python -m unittest discover -v

# Wipe our temporary workspace
cd ${cwd}
mkdir -p workspace
rm -Rf workspace/*
mkdir -p output_data
rm -Rf output_data/*

# Import test spectra
cd ${cwd}
cd import_grids/
python import_brani_grid.py
python import_apokasc.py

# Count number of CPU cores. This tell us how many copies of TurboSpectrum we can run at once.
n_cores_less_one=`cat /proc/cpuinfo | awk '/^processor/{print $3}' | tail -1`
n_cores=$((${n_cores_less_one} + 1))

# Synthesize test spectra
cd ${cwd}
cd synthesize_grids/
create="--create"  # Only create clean SpectrumLibrary in first thread
for item in `seq 0 ${n_cores_less_one}`
do
python synthesize_test.py --every ${n_cores} --skip ${item} ${create} \
                          --log-file ../output_data/turbospec_demo_stars_${item}.log &
sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
create="--no-create"
done
wait

# Synthesize APOKASC test set
#cd ${cwd}
#cd synthesize_grids/
#create="--create"  # Only create clean SpectrumLibrary in first thread
#for item in `seq 0 ${n_cores_less_one}`
#do
#python synthesize_apokasc.py --output-library turbospec_apokasc_test_set \
#                             --star-list ../../4MOST_testspectra/testset_param.tab \
#                             --log-file ../output_data/turbospec_apokasc_test_set_${item}.log \
#                             --every ${n_cores} --skip ${item} ${create} --limit 8 &
#sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
#create="--no-create"
#done
#wait

# Synthesize APOKASC training set
#cd ${cwd}
#cd synthesize_grids/
#create="--create"  # Only create clean SpectrumLibrary in first thread
#for item in `seq 0 ${n_cores_less_one}`
#do
#python synthesize_apokasc.py --output-library turbospec_apokasc_training_set \
#                             --star-list ../../4MOST_testspectra/trainingset_param.tab \
#                             --log-file ../output_data/turbospec_apokasc_training_set_${item}.log \
#                             --every ${n_cores} --skip ${item} ${create} --limit 8 &
#sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
#create="--no-create"
#done
#wait

# Copy synthesized APOKASC test set and training set
cd ${cwd}
rsync -av /mnt/data/ganymede_mirror/astrolabe/iwg7_pipeline/4most-4gp-scripts/workspace/turbospec_apokasc_* workspace

# Use 4FS to degrade the APOKASC spectra
cd ${cwd}
cd degrade_spectra
python degrade_apokasc_with_4fs.py --input-library turbospec_apokasc_training_set \
                                   --output-library-lrs 4fs_apokasc_training_set_lrs \
                                   --output-library-hrs 4fs_apokasc_training_set_hrs \
                                   --snr-list "250"

python degrade_apokasc_with_4fs.py --input-library turbospec_apokasc_test_set \
                                   --output-library-lrs 4fs_apokasc_test_set_lrs \
                                   --output-library-hrs 4fs_apokasc_test_set_hrs \
                                   --snr-list "5,10,15,20,50,100,250"

python degrade_apokasc_with_4fs.py --input-library turbospec_apokasc_test_set \
                                   --output-library-lrs 4fs_apokasc_test_set_lrs_snrperband \
                                   --output-library-hrs 4fs_apokasc_test_set_hrs_snrperband \
                                   --snr_definition "RH,4130,4150" \
                                   --snr_definition "GH,5435,5455" \
                                   --snr_definition "BH,6435,6455" \
                                   --snr_definition "RL,4503,4523" \
                                   --snr_definition "GL,6170,6190" \
                                   --snr_definition "BL,8255,8275" \
                                   --lrs_use_snr_definitions "RL,GL,BL" \
                                   --hrs_use_snr_definitions "RH,GH,BH" \
                                   --snr-list "5,10,15,20,50,100,250"

python degrade_apokasc_with_4fs.py --input-library turbospec_apokasc_test_set \
                                   --output-library-lrs 4fs_apokasc_test_set_lrs_snrperband_nored \
                                   --output-library-hrs 4fs_apokasc_test_set_hrs_snrperband_nored \
                                   --snr_definition "GH,5435,5455" \
                                   --snr_definition "BH,6435,6455" \
                                   --snr_definition "GL,6170,6190" \
                                   --snr_definition "BL,8255,8275" \
                                   --lrs_use_snr_definitions ",GL,BL" \
                                   --hrs_use_snr_definitions ",GH,BH" \
                                   --snr-list "5,10,15,20,50,100,250"

# Test RV determination
cd ${cwd}
cd test_rv_determination
python rv_test.py --test-count=3 --vary-mcmc-steps --output-file ../output_data/rv_test_vary_steps.out &
python rv_test.py --test-count=3 --output-file ../output_data/rv_test.out &
wait

# Test Cannon
cd ${cwd}
cd test_cannon_degraded_spec/

for mode in lrs hrs
do
for source in hawkins 4fs
do

python cannon_test.py --train ${source}_apokasc_training_set_${mode} \
                      --test ${source}_apokasc_test_set_${mode} \
                      --output-file ../output_data/cannon_test_${source}_${mode}

#python cannon_test.py --train ${source}_apokasc_training_set_${mode} \
#                      --test ${source}_apokasc_test_set_${mode} \
#                      --censor ../../4MOST_testspectra/ges_master_v5.fits \
#                      --output-file ../output_data/cannon_test_${source}_${mode}_censored

done
done

# Plot performance of RV code
cd ${cwd}
cd visualisation/rv_code/
for all in *.ppl ; do pyxplot ${all} ; done

cd visualisation/stellar_parameters/
for all in *.ppl ; do pyxplot ${all} ; done

cd ${cwd}
cd visualisation/cannon_performance
python plot_performance.py --library hawkins_apokasc_test_set_lrs --cannon-output ../../output_data/cannon_test_hawkins_lrs.dat --dataset-label "Hawkins LRS" \
                           --library hawkins_apokasc_test_set_hrs --cannon-output ../../output_data/cannon_test_hawkins_hrs.dat --dataset-label "Hawkins HRS" \
                           --library 4fs_apokasc_test_set_lrs --cannon-output ../../output_data/cannon_test_4fs_lrs.dat --dataset-label "Ford LRS" \
                           --library 4fs_apokasc_test_set_hrs --cannon-output ../../output_data/cannon_test_4fs_hrs.dat --dataset-label "Ford HRS"
