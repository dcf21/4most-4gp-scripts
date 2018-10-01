#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work
mkdir -p ../../../output_data/cannon

# -----------------------------------------------------------------------------------------

# Loop over both Gaussian and half ellipse convolutions
for convolution_kernel in gaussian half_ellipse
do

    # Do convolution for both 4MOST LRS and HRS
    for mode in hrs lrs
    do

        # Loop over two different SNRs
        for snr in 20 50
        do

            # Loop over different convolution widths for the test set
            for convolution_width in 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.1 2.2
            do


                python3 cannon_test.py --train "galah_training_sample_4fs_${convolution_kernel}_1.7_${mode}" \
                                       --test "galah_test_sample_4fs_${convolution_kernel}_${convolution_width}_${mode}_snr${snr}" \
                                       --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                                       --description "HRS with ${convolution_width}-pixel ${convolution_kernel} convolution; censored - 10 labels." \
                                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                                       --assume-scaled-solar \
                                       --output-file "../../../output_data/cannon/cannon_galah_${convolution_kernel}_${convolution_width}_censored_${mode}_10label_snr${snr}"

            done

        done

    done

done

