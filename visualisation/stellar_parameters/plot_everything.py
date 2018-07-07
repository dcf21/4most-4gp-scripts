#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python plot_everything.py>, but <./plot_everything.py> will not work.

"""
This script looks in the directory <4most-4gp-scripts/output_data/cannon> to see what tests you've run through the
Cannon and plots up the results automatically.
"""

import logging
import glob
from os import path as os_path

from lib import plot_settings
from lib.batch_processor import BatchProcessor

# Create logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "../../workspace")

# Create a long list of all the shell commands we want to run
batch = BatchProcessor(logger=logger,
                       output_path=os_path.join(our_path, "../../output_plots/stellar_parameters")
                       )

# Plot stellar parameter distributions in every spectrum library we have
libraries = sorted(glob.glob(os_path.join(workspace, "*")))
for i, library in enumerate(libraries):
    library_name = os_path.split(library)[1]

    # Keep user updated on progress
    logger.info("{:4d}/{:4d} Working on <{}>".format(i + 1, len(library) + 1, library_name))

    # Produce a scatter plot colour-coding the metallicity of the stars in a Kiel diagram
    batch.register_job(command="""
{python} scatter_plot_coloured.py \
    --library "{library}" \
    --label "Teff{{7000:3400}}" --label "logg{{5:0}}" --label "[Fe/H]{{:}}" \
    --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
    --colour-range-min 0.5 --colour-range-max -2
""".format(python=batch.python, library=library),

                       output="""
{library}/hr_coloured
""".format(library=library)
                       )

    # Produce a histogram of each label in turn
    batch.register_job(command="""
{python} histogram.py \
    --library ${library} \
    --label "Teff{{7000:3400}}" --label "logg{{5:0}}" --label "[Fe/H]{{1:-3}}" \
    --label-axis-latex "Teff" --label-axis-latex "log(g)" --label-axis-latex "[Fe/H]" \
    --using "\$1" --using "\$2" --using "\$3" \
    --output ../../output_plots/stellar_parameters/${library}/histogram
""".format(python=batch.python, library=library),

                       output="""
{library}/histogram
""".format(library=library)
                       )

# If we are not overwriting plots we've already made, then check which files already exist
if not plot_settings.overwrite_plots:
    batch.filter_jobs_where_products_already_exist()

# Report how many plots need making afresh
batch.report_status()

# Now run the shell commands
batch.run_jobs()
