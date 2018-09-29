#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python check_output_files_unique.py>, but <./check_output_files_unique.py> will not work.

"""
Check that the file <examples.sh> is not going to do multiple runs of the Cannon and save the output to the same
destination. I'm really bad at forgetting to change the destination filename when I create new tests, so this is a
useful check...
"""

import re

destinations = []

for line in open("examples_galah_20180416.sh"):
    line = line.strip()
    test = re.match("--output-file \"(.*)\"", line)
    if test is not None:
        destination = test.group(1)
        if destination in destinations:
            print("Clash for output <{}>".format(destination))
        else:
            destinations.append(destination)
