#!/bin/bash

# A little bit of scripting magic so that whatever directory this script is
# run from, we always find the python scripts and data we need.
cd "$(dirname "$0")"
cwd=`pwd`/..
cd ${cwd}

# Activate python virtual environment
source ../../../../virtualenv/bin/activate

# Now do some work

# Produce reddened versions of the demostration stars
python3 redden_library.py --input-library demo_stars \
                          --output-library demo_stars_reddened

# ------------------
# Redden the AHM2017 sample

python3 redden_library.py --input-library turbospec_ahm2017_perturbed \
                          --output-library reddened_ahm2017_perturbed

python3 degrade_library_with_4fs.py --input-library reddened_ahm2017_perturbed \
                                    --snr-list 50 \
                                    --output-library-lrs 4fs_reddened_ahm2017_perturbed_lrs \
                                    --output-library-hrs 4fs_reddened_ahm2017_perturbed_hrs

# ------------------
# Redden the GALAH sample

python3 redden_library.py --input-library galah_test_sample_turbospec \
                          --output-library galah_test_sample_reddened

python3 degrade_library_with_4fs.py --input-library galah_test_sample_reddened \
                                    --snr-list 50 \
                                    --mag-list 15 \
                                    --photometric-band "GROUND_JOHNSON_V" \
                                    --output-library-lrs galah_test_sample_reddened_4fs_snr50_lrs \
                                    --output-library-hrs galah_test_sample_reddened_4fs_snr50_hrs

python3 degrade_library_with_4fs.py --input-library galah_test_sample_reddened \
                                    --snr-list 50 \
                                    --mag-list 15 \
                                    --photometric-band "GROUND_JOHNSON_V" \
                                    --snr-definitions-hrs "GalDiskHR_536NM" \
                                    --no-run-lrs \
                                    --output-library-hrs galah_test_sample_reddened_4fs_snr50_s4grn_hrs

python3 degrade_library_with_4fs.py --input-library galah_test_sample_reddened \
                                    --snr-list 50 \
                                    --mag-list 15 \
                                    --photometric-band "GROUND_JOHNSON_V" \
                                    --snr-definitions-hrs "GalDiskHR_620NM" \
                                    --no-run-lrs \
                                    --output-library-hrs galah_test_sample_reddened_4fs_snr50_s4red_hrs

# ------------------
# Redden the 4TEAM sample

python3 redden_library.py --input-library turbospec_fourteam_sample \
                          --output-library reddened_fourteam_sample

python3 degrade_library_with_4fs.py --input-library reddened_fourteam_sample \
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

python3 degrade_library_with_4fs.py --input-library reddened_fourteam_sample \
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
# Redden the 4TEAM2 sample

python3 redden_library.py --input-library turbospec_fourteam2_sample \
                          --output-library reddened_fourteam2_sample

python3 degrade_library_with_4fs.py --input-library reddened_fourteam2_sample \
                                    --create \
                                    --mag-list 15 \
                                    --photometric-band "SDSS_g" \
                                    --snr-list "10,12,14,16,18,20,26,30,40,50,100,130,250" \
                                    --snr-per-angstrom \
                                    --snr-definition "A5354_5361,5354,5361" \
                                    --snr-definitions-lrs "A5354_5361" \
                                    --snr-definitions-hrs "A5354_5361" \
                                    --output-library-lrs 4fs_reddened_fourteam2_sample_lrs \
                                    --output-library-hrs 4fs_reddened_fourteam2_sample_hrs

