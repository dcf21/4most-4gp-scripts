#!/usr/bin/env bash
# -*- coding: utf-8 -*-

source ../../virtualenv/bin/activate

python rearrange.py --input-library 4fs_ges_dwarf_sample_lrs[SNR=100] \
                    --output-library tmp_ges_dwarf_A_lrs \
                    --output-library tmp_ges_dwarf_B_lrs \
                    --output-fraction 0.25 --output-fraction 0.75

python rearrange.py --input-library 4fs_ges_dwarf_sample_lrs[SNR=100] \
                    --contamination-library demo_stars[Starname=Sun] \
                    --contamination-fraction 0.1 \
                    --output-library tmp_ges_dwarf_A_lrs \
                    --output-library tmp_ges_dwarf_B_lrs \
                    --output-fraction 0.25 --output-fraction 0.75
