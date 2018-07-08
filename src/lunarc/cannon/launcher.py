#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python launcher.py>, but <./launcher.py> will not work.

"""
Take a list of training sets and test sets, and run the Cannon on them all using the SLURM job management system on
lunarc.

Note that before running this you may want to remove "diagnostics" from the list of modules imported by
<AnniesLasso/AnniesLasso/__init__.py>, as this requires matplotlib to be installed.

We do not allow the Cannon to run in multi-threaded mode, is empirically this causes us to exceed the memory limits
imposed on Aurora.
"""

import argparse
import os
import re
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
#
# job time, change for what your job requires
#SBATCH -t 150:00:00
#
# job name and output file names
#SBATCH -J cannon_{4}
#SBATCH -o stdout_cannon_{4}_%j.out
#SBATCH -e stderr_cannon_{4}_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

cd {0}
echo Starting rsync: `date`
echo Temporary directory: {1}
mkdir {1}
{2}
echo Rsync done: `date`
python cannon_test.py --workspace \"{1}\" {3}

"""

os.system("mkdir -p ../../output_data/cannon")

counter = 0
for job in args.jobs:
    config_path = os.path.split(os.path.abspath(job))[0]
    line_buffer = ""
    destination = ""
    libraries = []

    start_string = "python2.7 cannon_test.py"

    for line in open(job):
        line = line.strip()
        # Ignore blank lines and lines which begin with a hash
        if (len(line) == 0) or (line[0] == '#'):
            continue

        # Check for output destination
        test = re.match("--output-file \"(.*)\"", line)
        if test is not None:
            destination = test.group(1)

        # Check for spectrum libraries we need
        test = re.search("(?:--train|--test) \"([^\"\\[]*)([^\"]*)?\"", line)
        if test is not None:
            libraries.append(test.group(1))

        # Lines which end in backslashes append
        if line[-1] == "\\":
            line_buffer = "{} {}".format(line_buffer, line[:-1])
            continue

        # Put current line onto the end of line buffer
        line = "{} {}".format(line_buffer, line).strip()
        line_buffer = ""

        # Ignore shell commands which don't run Cannon tests
        if not line.startswith(start_string):
            continue

        # If file product already exists, don't need to recreate it
        destination = os.path.join(config_path, destination) + ".json"
        if os.path.exists(destination):
            print "Product <{}> already exists".format(destination)
            continue
        else:
            print "Product <{}> needs making".format(destination)

        # Create rsync command to copy spectrum libraries to node local storage
        run_id = "{}_{}".format(uid, counter)
        tmp_dir ="${{TMPDIR}}/cannon_{}".format(run_id)
        rsyncs = ["rsync -a ../workspace/{} {}/".format(library, tmp_dir) for library in libraries]
        rsync_commands = "\n".join(rsyncs)
        libraries = []

        command = line[len(start_string):]
        counter += 1
        slurm_tmp_filename = "tmp_{}.sh".format(run_id)

        with open(slurm_tmp_filename, "w") as f:
            f.write(slurm_script.format(config_path, tmp_dir, rsync_commands, command, os.path.split(destination)[1]))

        # os.system("sbatch {}".format(slurm_tmp_filename))

