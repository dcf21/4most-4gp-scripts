#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

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
            print "Clash for output <{}>".format(destination)
        else:
            destinations.append(destination)
