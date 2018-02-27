#!/bin/bash

# Activate python virtual environment
source ../../virtualenv/bin/activate

python2.7 redden_library.py --input-library demo_stars \
                            --output-library demo_stars_reddened \

python2.7 redden_library.py --input-library turbospec_ahm2017_perturbed \
                            --output-library reddened_ahm2017_perturbed \

python2.7 degrade_library_with_4fs.py --input-library reddened_ahm2017_perturbed \
                                      --snr-list 50 \
                                      --output-library-lrs 4fs_reddened_ahm2017_perturbed_lrs \
                                      --output-library-hrs 4fs_reddened_ahm2017_perturbed_hrs

# ------------------

python2.7 redden_library.py --input-library turbospec_fourteam_sample \
                            --output-library reddened_fourteam_sample

python2.7 degrade_library_with_4fs.py --input-library reddened_fourteam_sample \
                                      --create \
                                      --mag-list 13,15,16,19 \
                                      --photometric-band "GROUND_JOHNSON_V" \
                                      --snr-per-angstrom \
                                      --snr-definition "A4261_4270,4261,4270" \
                                      --snr-definitions-lrs "A4261_4270" \
                                      --snr-definitions-hrs "A4261_4270" \
                                      --snr-list "10,50,100,150" \
                                      --output-library-lrs 4fs_reddened_fourteam_sample_lrs \
                                      --output-library-hrs 4fs_reddened_fourteam_sample_hrs

python2.7 degrade_library_with_4fs.py --input-library reddened_fourteam_sample \
                                      --no-create \
                                      --mag-list 13,15,16,19 \
                                      --photometric-band "GROUND_JOHNSON_V" \
                                      --snr-per-angstrom \
                                      --snr-definition "A6190_6210,6190,6210" \
                                      --snr-definitions-lrs "A6190_6210" \
                                      --snr-definitions-hrs "A6190_6210" \
                                      --snr-list "10,50,100,150" \
                                      --output-library-lrs 4fs_reddened_fourteam_sample_lrs \
                                      --output-library-hrs 4fs_reddened_fourteam_sample_hrs

# ------------------

python2.7 redden_library.py --input-library turbospec_fourteam2_sample \
                            --output-library reddened_fourteam2_sample

python2.7 degrade_library_with_4fs.py --input-library reddened_fourteam2_sample \
                                      --create \
                                      --mag-list 15,15,15,15,15,15,15,15,15,15,15,15,15,15,15 \
                                      --photometric-band "SDSS_g" \
                                      --snr-list "10,12,14,16,18,20,23,26,30,35,40,45,50,80,100,130,180,250" \
                                      --snr-per-angstrom \
                                      --snr-definition "A5354_5361,5354,5361" \
                                      --snr-definitions-lrs "A5354_5361" \
                                      --snr-definitions-hrs "A5354_5361" \
                                      --output-library-lrs 4fs_reddened_fourteam2_sample_lrs \
                                      --output-library-hrs 4fs_reddened_fourteam2_sample_hrs

#python2.7 degrade_library_with_4fs.py --input-library reddened_fourteam2_sample \
#                                      --no-create \
#                                      --mag-list 15,15,15,15,15,15,15,15,15,15 \
#                                      --photometric-band "SDSS_g" \
#                                      --snr-per-angstrom \
#                                      --snr-definition "A6190_6210,6190,6210" \
#                                      --snr-definitions-lrs "A6190_6210" \
#                                      --snr-definitions-hrs "A6190_6210" \
#                                      --output-library-lrs 4fs_reddened_fourteam2_sample_lrs \
#                                      --output-library-hrs 4fs_reddened_fourteam2_sample_hrs
