#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work

# Loop over both Gaussian and half ellipse convolutions
for convolution_kernel in gaussian half_ellipse
do

    # Do convolution for both 4MOST LRS and HRS
    for mode in hrs lrs
    do

        python3 convolve_library.py --input-library galah_training_sample_4fs_${mode} \
                                    --kernel ${convolution_kernel} \
                                    --width 1.7 \
                                    --output-library galah_training_sample_4fs_${convolution_kernel}_1.7_${mode} \
                                    --db-in-tmp

        # Loop over two different SNRs
        for snr in 20 50
        do

            # Loop over different convolution widths for the test set
            for convolution_width in 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.1 2.2
            do

                python3 convolve_library.py --input-library "galah_test_sample_4fs_${mode}[SNR=${snr}]" \
                                            --kernel ${convolution_kernel} \
                                            --width ${convolution_width} \
                                            --output-library galah_test_sample_4fs_${convolution_kernel}_${convolution_width}_${mode}_snr${snr} \
                                            --db-in-tmp

            done

        done

    done

done

