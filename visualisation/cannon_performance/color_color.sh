#!/bin/bash

source ../../../virtualenv/bin/activate

python color_color.py --library 4fs_apokasc_test_set_hrs --output-file /tmp/tg_test_hrs_ --cannon_output ../../output_data/cannon_test_4fs_hrs.dat 
python color_color.py --library 4fs_apokasc_test_set_lrs --output-file /tmp/tg_test_lrs_ --cannon_output ../../output_data/cannon_test_4fs_lrs.dat 
python color_color.py --library 4fs_apokasc_training_set_hrs --output-file /tmp/tg_train_hrs_
python color_color.py --library 4fs_apokasc_training_set_lrs --output-file /tmp/tg_train_lrs_
