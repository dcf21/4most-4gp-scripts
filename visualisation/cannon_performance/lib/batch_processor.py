# -*- coding: utf-8 -*-

"""
A class which allows us to run batches of shell commands in parallel.
"""

from os import path as os_path
import sys


class BatchProcessor:
    """
    A class which allows us to run batches of shell commands in parallel.
    """

    def __init__(self, logger, output_path):
        self.logger = logger
        self.output_path = output_path
        self.python = sys.executable
        self.job_list = []

    def register_job(self, script, arguments, substitutions, output):
        self.job_list.append({"script": script,
                              "arguments": arguments,
                              "substitutions": substitutions,
                              "output": output,
                              "needs_doing": True
                              })

    def filter_jobs_where_products_already_exist(self):
        # Check which file products already exist and don't need to be remade
        for item in self.job_list:
            if item["needs_doing"]:
                item["needs_doing"] = not os_path.exists(os_path.join(self.output_path, item["output"]))

    def report_status(self):
        # Report how many plots need making afresh
        self.logger.info("Making {:d} plots.".format(sum([i["needs_doing"] for i in self.job_list])))

        self.logger.info("Not making {:d} plots, because they are already made.".
                         format(sum([not i["needs_doing"] for i in self.job_list])))

    def run_jobs(self):
        # Now run the shell commands
        pass
