#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take a list of training sets and test sets, and run the Cannon on them all using the SLURM job management system on
lunarc.
"""

import argparse
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--job_list', action="append", dest='jobs',
                    help="List of spectrum libraries we should run the Cannon on.")
args = parser.parse_args()

uid = os.getpid()

slurm_script = """#!/bin/sh
# requesting the number of nodes needed
#SBATCH -N 1
#SBATCH --exclusive
#SBATCH --tasks-per-node=20
#
# job time, change for what your job requires
#SBATCH -t 01:00:00
#
# job name and output file names
#SBATCH -J cannon_farm
#SBATCH -o stdout_cannon_%j.out
#SBATCH -e stderr_cannon_%j.out
cat $0

module add GCC/5.4.0-2.26  OpenMPI/1.10.3  scipy/0.17.0-Python-2.7.11  SQLite/3.20.1  SQLite/3.9.2

cd ${{HOME}}/iwg7_pipeline/4most-4gp-scripts/test_cannon_degraded_spec
python cannon_test.py --train "{}" --test "{}" --output-file "../output_data/{}" --tolerance {}

"""

counter = 0
for job in args.jobs:
    for line in open(job):
        # Ignore blank lines and lines which begin with a hash
        if (len(line.strip()) == 0) or (line.strip()[0] == '#'):
            continue

        counter += 1
        words = line.split()
        assert len(words) == 4

        training = words[0]
        test = words[1]
        output = words[2]
        tolerance = float(words[3])

        slurm_tmp_filename = "tmp_{}_{}.sh".format(uid, counter)

        with open(slurm_tmp_filename, "w") as f:
            f.write(slurm_script.format(training, test, output, tolerance))

        os.system("sbatch {}".format(slurm_tmp_filename))

