# -*- coding: utf-8 -*-

"""
A class which allows us to run batches of shell commands in parallel.
"""

import os
from os import path as os_path
import sys
import multiprocessing as mp


class BatchProcessor:
    """
    A class which allows us to run batches of shell commands in parallel.
    """

    def __init__(self, logger, output_path):
        """
        Instantiate an object for running many python scripts in parallel.

        :param logger:
            A logger object
        :param output_path:
            The path, relative to which the output of each individual python script should be specified. Below, we
            inform each python script where to direct its output via a --output <filename> command line argument
            which we assume every python script to accept. We also use this filename to determine which scripts have
            already produced output, so that we can choose not to run them again.
        :type output_path:
            str
        """
        self.logger = logger
        self.output_path = output_path
        self.python = sys.executable
        self.job_list = []

    def register_job(self, script, arguments, substitutions, output):
        """
        Register a job (i.e. a python command line) that we should run in parallel with others.

        :param script:
            The name of the python script we should run
        :type script:
            str
        :param arguments:
            A dictionary of the command line arguments we should pass to the python script. Values may be specified
            either as strings, or as lists if the command line argument is to be repeated multiple times.
        :type arguments:
            dict
        :param substitutions:
            A dictionary of substitutions which we should make within the above parameters. In both the names and
            values of command line arguments, we can write {keyword}, and have that keyword substituted by a value
            in this dictionary.
        :type substitutions:
            dict
        :param output:
            The filename of the output that this python script should produce. We pass this filename to the script via
            the command line argument --output <filename>. We also use this to determine whether the script has
            already produced output.
        :type output:
            str
        :return:
            None
        """
        self.job_list.append({"script": script,
                              "arguments": arguments,
                              "substitutions": substitutions,
                              "output": output,
                              "needs_doing": True
                              })

    def filter_jobs_where_products_already_exist(self):
        """
        Filter out any jobs which have been queued, but which would overwrite existing output. Call this method if
        you do not want to rerun jobs which have already been run.

        :return:
            None
        """
        # Check which file products already exist and don't need to be remade
        for item in self.job_list:
            if item["needs_doing"]:
                item["needs_doing"] = not os_path.exists(os_path.join(self.output_path, item["output"]))

    def report_status(self):
        """
        Report to the user how many python scripts we have queued to run.

        :return:
            None
        """
        # Report how many plots need making afresh
        plots_to_make = sum([i["needs_doing"] for i in self.job_list])
        self.logger.info("Making {:d} plots.".format(plots_to_make))

        plots_not_being_made = sum([not i["needs_doing"] for i in self.job_list])
        if plots_not_being_made > 0:
            self.logger.info("{:d} plots are not being remade, because they already exist.".
                             format(plots_not_being_made))

    def list_shell_commands(self):
        """
        Convert the job decriptors supplied to register_job() into fully-formed shell commands.

        :return:
            List of strings, containing the shell commands which are to be executed
        """
        shell_commands = []

        for item in self.job_list:
            if item["needs_doing"]:
                shell_command = ("{python} {script} --output \"{output_path}/{output}\" ".
                                 format(python=self.python,
                                        script=item["script"],
                                        output_path=self.output_path,
                                        output=item["output"].format(**item["substitutions"])
                                        ))

                for argument_name in sorted(item["arguments"].keys()):
                    argument_values = item["arguments"][argument_name]

                    if not isinstance(argument_values, (list, tuple)):
                        argument_values = [argument_values]

                    for value in argument_values:
                        shell_command += ("--{name} \"{value}\" ".
                                          format(name=argument_name.format(**item["substitutions"]),
                                                 value=str(value).format(**item["substitutions"])
                                                 ))
                shell_commands.append(shell_command)
        return shell_commands

    def list_shell_commands_to_file(self, filename):
        """
        Write to a log file the complete list of shell commands that we're going to run.

        :param filename:
            The filename of the log file to which we should save our output
        :type filename:
            str
        :return:
            None
        """
        with open(filename, "w") as output:
            for command in self.list_shell_commands():
                output.write("{}\n".format(command))

    def run_jobs(self):
        """
        Run the python scripts which we have queued up.

        :return:
            None
        """

        # Set up the parallel task pool to use half the available processors
        count = mp.cpu_count() / 2
        pool = mp.Pool(processes=count)

        # Run the jobs
        pool.map(func=worker,
                 iterable=self.list_shell_commands()
                 )


# Helper to run the shell commands. This has to be globally defined so all the threads can see it...
def worker(job_item):
    os.system(job_item)
