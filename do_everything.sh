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
cd ${cwd}
cd synthesize_grids/
create="--create"  # Only create clean SpectrumLibrary in first thread
for item in `seq 0 ${n_cores_less_one}`
do
python synthesize_apokasc.py --output-library turbospec_apokasc_test_set \
                             --star-list ../../4MOST_testspectra/testset_param.tab \
                             --log-file ../output_data/turbospec_apokasc_test_set_${item}.log \
                             --every ${n_cores} --skip ${item} ${create} &
sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
create="--no-create"
done
wait

# Synthesize APOKASC training set
cd ${cwd}
cd synthesize_grids/
create="--create"  # Only create clean SpectrumLibrary in first thread
for item in `seq 0 ${n_cores_less_one}`
do
python synthesize_apokasc.py --output-library turbospec_apokasc_training_set \
                             --star-list ../../4MOST_testspectra/trainingset_param.tab \
                             --log-file ../output_data/turbospec_apokasc_training_set_${item}.log \
                             --every ${n_cores} --skip ${item} ${create} &
sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
create="--no-create"
done
wait

# Synthesize dwarf stars
cd ${cwd}
cd synthesize_grids/
create="--create"  # Only create clean SpectrumLibrary in first thread
for item in `seq 0 ${n_cores_less_one}`
do
python synthesize_ges_dwarfs.py --output-library turbospec_ges_dwarf_sample \
                                --star-list ../../downloads/GES_iDR5_WG15_Recommended.fits \
                                --log-file ../output_data/turbospec_ges_dwarfs_${item}.log \
                                --every ${n_cores} --skip ${item} ${create} &
sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
create="--no-create"
done
wait

# Synthesize AHM2017 sample of GES stars
cd ${cwd}
cd synthesize_grids/
create="--create"  # Only create clean SpectrumLibrary in first thread
for item in `seq 0 ${n_cores_less_one}`
do
python synthesize_ahm2017.py --output-library turbospec_ahm2017_sample \
                             --star-list ../../downloads/GES_iDR5_WG15_Recommended.fits \
                             --log-file ../output_data/turbospec_ahm2017_${item}.log \
                             --every ${n_cores} --skip ${item} ${create} &
sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
create="--no-create"
done
wait

# Synthesize grid of stars on MARCS grid of parameter values
cd ${cwd}
cd synthesize_grids/
create="--create"  # Only create clean SpectrumLibrary in first thread
for item in `seq 0 ${n_cores_less_one}`
do
python synthesize_marcs_grid.py --log-file ../output_data/turbospec_marcs_grid_${item}.log \
                                --every ${n_cores} --skip ${item} ${create} &
sleep 2  # Wait 2 seconds before launching next thread, to check SpectrumLibrary has appeared
create="--no-create"
done
wait

# Use 4FS to degrade the APOKASC spectra
cd ${cwd}
cd degrade_spectra
for mode in training_set test_set
do
python degrade_library_with_4fs.py --input-library turbospec_apokasc_${mode} \
                                   --output-library-lrs 4fs_apokasc_${mode}_lrs \
                                   --output-library-hrs 4fs_apokasc_${mode}_hrs

python degrade_library_with_4fs.py --input-library turbospec_apokasc_${mode} \
                                   --output-library-lrs 4fs_apokasc_${mode}_lrs_snrperband \
                                   --output-library-hrs 4fs_apokasc_${mode}_hrs_snrperband \
                                   --snr-definition "BH,4130,4150" \
                                   --snr-definition "GH,5435,5455" \
                                   --snr-definition "RH,6435,6455" \
                                   --snr-definition "BL,4503,4523" \
                                   --snr-definition "GL,6170,6190" \
                                   --snr-definition "RL,8255,8275" \
                                   --snr-definitions-lrs "RL,GL,BL" \
                                   --snr-definitions-hrs "RH,GH,BH"

python degrade_library_with_4fs.py --input-library turbospec_apokasc_${mode} \
                                   --output-library-lrs 4fs_apokasc_${mode}_lrs_snrperband_noblue \
                                   --output-library-hrs 4fs_apokasc_${mode}_hrs_snrperband_noblue \
                                   --snr-definition "GH,5435,5455" \
                                   --snr-definition "RH,6435,6455" \
                                   --snr-definition "GL,6170,6190" \
                                   --snr-definition "RL,8255,8275" \
                                   --snr-definitions-lrs "RL,GL," \
                                   --snr-definitions-hrs "RH,GH,"
done

python degrade_library_with_4fs.py --input-library turbospec_ges_dwarf_sample \
                                   --output-library-lrs 4fs_ges_dwarf_sample_lrs \
                                   --output-library-hrs 4fs_ges_dwarf_sample_hrs

python degrade_library_with_4fs.py --input-library turbospec_ahm2017_sample \
                                   --output-library-lrs 4fs_ahm2017_sample_lrs \
                                   --output-library-hrs 4fs_ahm2017_sample_hrs

python degrade_library_with_4fs.py --input-library demo_stars \
                                   --output-library-lrs 4fs_demo_stars_lrs \
                                   --output-library-hrs 4fs_demo_stars_hrs

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
for settings in '' '_snrperband' '_snrperband_noblue'
do

python cannon_test.py --train ${source}_apokasc_training_set_${mode}${settings} \
                      --test ${source}_apokasc_test_set_${mode}${settings} \
                      --output-file ../output_data/cannon_test_${source}_${mode}${settings}

#python cannon_test.py --train ${source}_apokasc_training_set_${mode}${settings} \
#                      --test ${source}_apokasc_test_set_${mode}${settings} \
#                      --censor ../../4MOST_testspectra/ges_master_v5.fits \
#                      --output-file ../output_data/cannon_test_${source}_${mode}${settings}_censored

done
done
done

# Plot performance of RV code
cd ${cwd}
cd visualisation/rv_code/
for all in *.ppl ; do pyxplot ${all} ; done

cd visualisation/stellar_parameters/
for all in *.ppl ; do pyxplot ${all} ; done

# Plot performance of Cannon
cd ${cwd}
cd visualisation/cannon_performance
python plot_performance.py --library hawkins_apokasc_test_set_lrs --cannon-output ../../output_data/cannon_test_hawkins_lrs.dat --dataset-label "Hawkins LRS" \
                           --library hawkins_apokasc_test_set_hrs --cannon-output ../../output_data/cannon_test_hawkins_hrs.dat --dataset-label "Hawkins HRS" \
                           --library 4fs_apokasc_test_set_lrs --cannon-output ../../output_data/cannon_test_4fs_lrs.dat --dataset-label "Ford LRS" \
                           --library 4fs_apokasc_test_set_hrs --cannon-output ../../output_data/cannon_test_4fs_hrs.dat --dataset-label "Ford HRS"
