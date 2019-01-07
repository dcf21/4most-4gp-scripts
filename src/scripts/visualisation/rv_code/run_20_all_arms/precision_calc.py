#!../../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python precision_calc.py>, but <./precision_calc.py> will not work.

import glob
import re

import numpy as np
from filters import filters

precision_targets = [5000, 2000, 1000]

# Read index of runs
run_index = {}
run_pids = []
for line in open("data/run_index.dat"):
    line = line.strip()

    # Ignore blank lines
    if line == "" or line[0] == "#":
        continue

    words = line.split()
    run_letter = words[0]
    run_pid = words[1]
    run_description = line[14:]

    run_index[run_pid] = [run_letter, run_pid, run_description]
    run_pids.append(run_pid)

# Loop over data files one by one
for pid in run_pids:
    for filename in sorted(glob.glob("data/*_{}.dat".format(pid))):
        test = re.search(r"_(...)_(\d*).dat", filename)
        if test is None:
            continue
        arm_name = test.group(1)
        pid = test.group(2)

        run_info = run_index[pid]

        print("\n# {}) {} -- {}".format(run_info[0], run_info[2], arm_name))

        for filter_info in filters:
            print("  * {}".format(filter_info[0]))
            samples_total = 0
            samples_within_precision = [0] * len(precision_targets)
            data = []
            for line in open(filename):
                line = line.strip()

                if len(line) == 0 or line[0] == '#':
                    continue

                words = line.split()

                if filter_info[1] is not None:
                    if not filter_info[2] <= float(words[filter_info[1]]) <= filter_info[3]:
                        continue

                rv_error = (float(words[8]) - float(words[7])) * 1000

                samples_total += 1
                for i, precision_target in enumerate(precision_targets):
                    if abs(rv_error) < precision_target:
                        samples_within_precision[i] += 1

                data.append(rv_error)

            print("    * Total samples: {:7d}".format(samples_total))
            if samples_total == 0:
                continue

            for i, precision_target in enumerate(precision_targets):
                print("    * RVs recovered to within {:5d} m/s: {:7d} ({:5.1f} %)".format(
                    precision_target,
                    samples_within_precision[i],
                    samples_within_precision[i] / samples_total * 100
                ))

            data.sort()
            data = np.array(data[10:-10])  # Exclude extreme data points
            print("    * Mean of RV errors (systematic bias): {:10.4f}".format(np.mean(data)))
            print("    * Standard deviation of RV errors (\"precision\"): {:10.4f}".format(np.std(data)))
