#!../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python run_pipeline_on_spectrum_library.py>, but <./run_pipeline_on_spectrum_library.py> will not work.

"""
Run the contents of a spectrum library through the 4GP pipeline.
"""

import argparse
import logging
from os import path as os_path

from fourgp_pipeline import PipelineFGK
from fourgp_pipeline import PipelineManager
from fourgp_speclib import SpectrumLibrarySqlite


# Implement a pipeline manager which loads spectra for analysis from disk
class PipelineManagerReadFromSpectrumLibrary(PipelineManager):
    """
    A pipeline manager which loads spectra for analysis from a spectrum library.
    """

    def __init__(self, spectrum_library_to_analyse, workspace, pipeline):
        """
        Open the spectrum library containing the spectra that we are to analyse.

        :param spectrum_library_to_analyse:
            The name of the spectrum library we are to analyse
        :type spectrum_library_to_analyse:
            str
        :param workspace:
            Directory where we expect to find spectrum libraries.
        :type workspace:
            str
        :param pipeline:
            The Pipeline we are to run spectra through.
        :type pipeline:
            Pipeline
        """

        # Initialise pipeline manager
        super(PipelineManagerReadFromSpectrumLibrary, self).__init__(pipeline=pipeline)

        # Open the spectrum library we are reading from
        self.spectrum_library_to_analyse = spectrum_library_to_analyse

        spectra = SpectrumLibrarySqlite.open_and_search(
            library_spec=spectrum_library_to_analyse,
            workspace=workspace,
            extra_constraints={}
        )
        input_library, input_library_items = [spectra[i] for i in ("library", "items")]

        input_library_ids = [i["specId"] for i in input_library_items]

        self.input_library = input_library
        self.input_library_items = input_library_items
        self.input_library_ids = input_library_ids
        self.spectrum_counter = 0

    def fetch_work(self):
        """
        Check to see if we have any spectra to analyse. If yes, return the next Spectrum object which needs
        analysing. If we have nothing to do, return None.

        :return:
            Spectrum object to be analysed
        """

        # If we have done all the spectra already, return None
        if self.spectrum_counter >= len(self.input_library_items):
            return None

        # Fetch next spectrum to analyse
        test_spectrum_array = self.input_library.open(ids=self.input_library_ids[self.spectrum_counter])
        spectrum = test_spectrum_array.extract_item(0)
        spectrum_id = spectrum.metadata['uid']

        return {
            'spectrum': spectrum,
            'spectrum_identifier': spectrum_id
        }

    def post_result(self, spectrum_analysis):
        """
        Post the results from analysing a spectrum back to whatever database you are using to store the pipeline's
        output

        :param spectrum_analysis:
            A SpectrumAnalysis object containing the results of the pipeline's analysis of the spectrum.
        :type spectrum_analysis:
            SpectrumAnalysis
        :return:
            True for success; False for failure.
        """

        # This method should save the output of the pipeline somewhere

        # Don't bother doing anything with the output for now
        return True


def main(logger, input_library, workspace, fourmost_mode, reload_cannon):
    """
    Main entry point for running the pipeline.

    :param logger:
        Logging object used to update user on progress of pipeline.
    :param input_library:
        The name of the spectrum library whose contents we are to run the pipeline on.
    :param workspace:
        The path of the workspace directory containing the spectrum libraries we are to use.
    :param fourmost_mode:
        The name of the 4MOST mode we are operating, either hrs or lrs
    :param reload_cannon:
        The filename of the output files containing the trained Cannon that we are to reload.
    :return:
        None
    """

    # Let user know we're up and running
    logger.info("Running FGK pipeline on the spectrum library <{}>".format(input_library))

    # Set path to workspace where we expect to find libraries of spectra
    our_path = os_path.split(os_path.abspath(__file__))[0]
    workspace = workspace if workspace else os_path.join(our_path, "../../../workspace")

    # Instantiate the pipeline
    pipeline = PipelineFGK(
        workspace=workspace,
        fourmost_mode=fourmost_mode,
        reload_cannon_from_file=reload_cannon
    )

    # Instantiate the pipeline manager
    pipeline_manager = PipelineManagerReadFromSpectrumLibrary(
        spectrum_library_to_analyse=input_library,
        workspace=workspace,
        pipeline=pipeline
    )

    # Do the work
    while pipeline_manager.poll_server_for_work():
        pass


# Do it right away if we're run as a script
if __name__ == "__main__":
    # Configure format for logging messages
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', required=True, dest='input_library',
                        help="Library of spectra to pipeline is to work on. Stars may be filtered by parameters by "
                             "placing a comma-separated list of constraints in [] brackets after the name of the "
                             "library. Use the syntax [Teff=3000] to demand equality, or [0<[Fe/H]<0.2] to specify a "
                             "range.")
    parser.add_argument('--workspace', dest='workspace', default="",
                        help="Directory where we expect to find spectrum libraries.")
    parser.add_argument('--reload-cannon', required=True, dest='reload_cannon',
                        help="Filename of a trained Cannon that we are to reload.")
    parser.add_argument('--output-file', default="./test_cannon.out", dest='output_file',
                        help="Data file to write output to.")
    parser.add_argument('--mode', required=True, dest='fourmost_mode',
                        choices=("hrs", "lrs"),
                        help="The 4MOST mode we are operating on.")
    args = parser.parse_args()

    main(logger=logger,
         input_library=args.input_library,
         workspace=args.workspace,
         reload_cannon=args.reload_cannon,
         fourmost_mode=args.fourmost_mode
         )
