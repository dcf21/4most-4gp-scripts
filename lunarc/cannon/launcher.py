#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Take a list of training sets and test sets, and run the Cannon on them all using the SLURM job management system on
lunarc.

Note that before running this you may want to remove "diagnostics" from the list of modules imported by
<AnniesLasso/AnniesLasso/__init__.py>, as this requires matplotlib to be installed.
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
#SBATCH --tasks-per-node=4
#
# job time, change for what your job requires
#SBATCH -t 06:00:00
#
# job name and output file names
#SBATCH -J cannon_farm
#SBATCH -o stdout_cannon_%j.out
#SBATCH -e stderr_cannon_%j.out
cat $0

module add GCC/5.4.0-2.26  OpenMPI/1.10.3  scipy/0.17.0-Python-2.7.11  SQLite/3.20.1  SQLite/3.9.2

export PYTHONPATH=${{HOME}}/local/lib/python2.7/site-packages:${{PYTHONPATH}}

cd ${{HOME}}/iwg7_pipeline/4most-4gp-scripts/test_cannon_degraded_spec
python cannon_test.py {}

"""

os.system("mkdir -p ../../output_data/cannon")

counter = 0
for job in args.jobs:
    line_buffer = ""
    for line in open(job):
        line = line.strip()
        # Ignore blank lines and lines which begin with a hash
        if (len(line) == 0) or (line[0] == '#'):
            continue

        # Lines which end in backslashes append
        if line[-1] == "\\":
            line_buffer = "{} {}".format(line_buffer, line[:-1])
            continue

        # Put current line onto the end of line buffer
        line = "{} {}".format(line_buffer, line).strip()
        line_buffer = ""

        # Ignore shell commands which don't run Cannon tests
        if not line.startswith("python cannon_test.py"):
            continue

        command = line[22:]
        counter += 1
        slurm_tmp_filename = "tmp_{}_{}.sh".format(uid, counter)

        with open(slurm_tmp_filename, "w") as f:
            f.write(slurm_script.format(command))

        os.system("sbatch {}".format(slurm_tmp_filename))

