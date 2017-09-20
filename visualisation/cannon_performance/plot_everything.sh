#!/bin/bash

source ../../../virtualenv/bin/activate

python scatter_plot_arrows.py --library 4fs_apokasc_test_set_hrs --output-file /tmp/tg_test_hrs_ \
                              --cannon_output ../../output_data/cannon_test_4fs_hrs.dat

python scatter_plot_arrows.py --library 4fs_apokasc_test_set_lrs --output-file /tmp/tg_test_lrs_ \
                              --cannon_output ../../output_data/cannon_test_4fs_lrs.dat
