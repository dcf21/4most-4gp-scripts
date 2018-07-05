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

import os
import sys
import logging
import re
import glob
import json
from os import path as os_path

from lib.label_information import LabelInformation

# Create logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

# Set path to workspace where we expect to find libraries of spectra
our_path = os_path.split(os_path.abspath(__file__))[0]
workspace = os_path.join(our_path, "../../output_data/cannon")

# Path to python binary
python_path = sys.executable

# Output directory
output_path = os_path.join(our_path, "../../output_plots/cannon_performance")

# Create output directories
targets = ["arrows", "performance_vs_label", "uncertainties", "required_snrA", "required_snrB", "label_offsets"]

for target in targets:
    os.system("mkdir -p {}".format(target))

# We run most jobs for both 4MOST LRS and HRS
modes_4most = ["hrs", "lrs"]

# Create a long list of all the shell commands we want to run
jobs = []

# comparison_censoring_schemes_*
# Create plots of the relative performance of the 4 censoring schemes, trained and tested on UVES or GALAH
for mode in modes_4most:
    for run in ["ahm2017_perturbed", "galah"]:
        jobs.append("""
{python} mean_performance_vs_label.py \
  --plot-width 14 --hide-date \
  --cannon-output "{data_path}/cannon_{sample}_{mode}_10label.json" --dataset-label "No censoring" --dataset-colour "green" \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-label "Censoring scheme 1" --dataset-colour "blue" \
  --cannon-output "{data_path}/cannon_{sample}_censored2_{mode}_10label.json" --dataset-label "Censoring scheme 2" --dataset-colour "red" \
  --cannon-output "{data_path}/cannon_{sample}_censored3_{mode}_10label.json" --dataset-label "Censoring scheme 3" --dataset-colour "purple" \
  --output-file "{out_path}/comparison_censoring_schemes_{sample}_{mode}"
""".format(python=python_path, mode=mode, sample=run,
           data_path=workspace, out_path=os_path.join(output_path, "performance_vs_label")))

# comparison_low_z_*
# Create a plot of the performance of the Cannon, when trained and tested on the [Fe/H] < -1 and [Fe/H] > 1 regimes
# separately
for mode in modes_4most:
    for run in ["ahm2017_perturbed", "galah"]:
        jobs.append("""
{python} mean_performance_vs_label.py \
  --plot-width 14 --hide-date \
  --cannon-output "{data_path}/cannon_{sample}_fehcut2_{mode}_10label.json" --dataset-filter "[Fe/H]<-1" --dataset-label "Trained \$z<-1\$ only" --dataset-colour "green" \
  --cannon-output "{data_path}/cannon_{sample}_{mode}_10label.json" --dataset-filter "[Fe/H]<-1" --dataset-label "Trained on full sample" --dataset-colour "red" \
  --output-file "../../output_plots/cannon_performance/performance_vs_label/comparison_low_z_{sample}_{mode}"
""".format(python=python_path, mode=mode, sample=run,
           data_path=workspace, out_path=os_path.join(output_path, "performance_vs_label")))

# comparisonA -- Plot the performance of the Cannon for different types of stars -- giants and dwarfs, metal rich and
# metal poor
for mode in modes_4most:
    for run in ["ahm2017_perturbed", "galah"]:
        for divisor in ["h", "fe"]:
            jobs.append("""
{python} mean_performance_vs_label.py \
  --plot-width 14 --hide-date \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>0;[Fe/H]<1" --dataset-label "Giants; [Fe/H]\$>0\$" --dataset-colour "purple" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>0;[Fe/H]<1" --dataset-label "Dwarfs; [Fe/H]\$>0\$" --dataset-colour "magenta" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>-0.5;[Fe/H]<0" --dataset-label "Giants; \$-0.5<\$[Fe/H]\$<0\$" --dataset-colour "blue" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>-0.5;[Fe/H]<0" --dataset-label "Dwarfs; \$-0.5<\$[Fe/H]\$<0\$" --dataset-colour "red" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>-1;[Fe/H]<-0.5" --dataset-label "Giants; \$-1<\$[Fe/H]$<-0.5$" --dataset-colour "cyan" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>-1;[Fe/H]<-0.5" --dataset-label "Dwarfs; \$-1<\$[Fe/H]$<-0.5$" --dataset-colour "orange" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg<3.25;[Fe/H]>-2;[Fe/H]<-1" --dataset-label "Giants; [Fe/H]$<-1$" --dataset-colour "green" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-filter "logg>3.25;[Fe/H]>-2;[Fe/H]<-1" --dataset-label "Dwarfs; [Fe/H]$<-1$" --dataset-colour "brown" --dataset-linetype 1 \
  --abundances-over-{divisor} \
  --output-file "{out_path}/comparisonA_{sample}_{mode}_{divisor}"
""".format(python=python_path, mode=mode, sample=run, divisor=divisor,
           data_path=workspace, out_path=os_path.join(output_path, "performance_vs_label")))

# comparisonB -- Plot the performance of the Cannon when fitting 3 or 10 parameters
for mode in modes_4most:
    for run in ["ahm2017_perturbed", "galah"]:
        for divisor in ["h", "fe"]:
            jobs.append("""
{python} mean_performance_vs_label.py \
  --cannon-output "{data_path}/cannon_{sample}_{mode}_3label.json" --dataset-label "3 parameter; uncensored" --dataset-colour "green" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_{mode}_4label.json" --dataset-label "4 parameter; uncensored" --dataset-colour "blue" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_{mode}_5label.json" --dataset-label "5 parameter; uncensored" --dataset-colour "orange" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_{mode}_10label.json" --dataset-label "10 parameters; uncensored" --dataset-colour "red" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_{mode}_12label.json" --dataset-label "12 parameters; uncensored" --dataset-colour "purple" --dataset-linetype 1 \
  --abundances-over-{divisor} \
  --output-file "{out_path}/comparisonB_{sample}_{mode}_{divisor}"
""".format(python=python_path, mode=mode, sample=run, divisor=divisor,
           data_path=workspace, out_path=os_path.join(output_path, "performance_vs_label")))

            jobs.append("""
{python} mean_performance_vs_label.py \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_3label.json" --dataset-label "3 parameter; censored" --dataset-colour "blue" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_4label.json" --dataset-label "4 parameter; censored" --dataset-colour "green" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_5label.json" --dataset-label "5 parameter; censored" --dataset-colour "orange" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_10label.json" --dataset-label "10 parameters; censored" --dataset-colour "red" --dataset-linetype 1 \
  --cannon-output "{data_path}/cannon_{sample}_censored_{mode}_12label.json" --dataset-label "12 parameters; censored" --dataset-colour "purple" --dataset-linetype 1 \
  --abundances-over-{divisor} \
  --output-file "{out_path}/comparisonB_{sample}_{mode}_censored_{divisor}"
""".format(python=python_path, mode=mode, sample=run, divisor=divisor,
           data_path=workspace, out_path=os_path.join(output_path, "performance_vs_label")))

# Now plot performance vs SNR for every Cannon run we have
cannon_runs = sorted(glob.glob(os_path.join(workspace, "*.json")))
for i, cannon_output in enumerate(cannon_runs):

    # Keep user updated on progress
    logger.info("{:4d}/{:4d} Working out jobs for <{}>".format(i + 1, len(cannon_runs) + 1, cannon_output))

    # Extract name of Cannon run from filename
    test = re.match(os_path.join(workspace, r"(.*).json"), cannon_output)
    cannon_run = test.group(1)

    # Produce a plot of precision vs SNR
    jobs.append("""
{python} mean_performance_vs_label.py \
  --plot-width 14 --hide-date \
  --cannon-output "{cannon_output}" \
  --output-file "{out_path}/{cannon_run}"
""".format(python=python_path, cannon_output=cannon_output, cannon_run=cannon_run,
           data_path=workspace, out_path=os_path.join(output_path, "performance_vs_label")))

    # Produce a scatter plot of the nominal uncertainties in the Cannon's label estimates
    jobs.append("""
{python} scatter_plot_cannon_uncertainty.py --cannon-output "{cannon_output}" \
  --output-stub "../../output_plots/cannon_performance/uncertainties/{cannon_run}"
""".format(python=python_path, cannon_output=cannon_output, cannon_run=cannon_run,
           data_path=workspace, out_path=os_path.join(output_path, "performance_vs_label")))

    # Now produce scatter plots of the SNR required to achieve the target precision in each label for each star
    label_info = LabelInformation().label_info
    cannon_output_data = json.loads(open(cannon_output).read())
    label_names = [item for item in cannon_output_data['labels'] if item in label_info]
    for colour_label in label_names:
        # Figure out the target precision for each label, and units
        target_accuracy = label_info[colour_label]['targets'][0]
        target_unit = label_info[colour_label]['unit']

        # Produce a version of each label which is safe to put in the filename of a file
        path_safe_label = re.sub(r"\[(.*)/H\]", r"\g<1>", colour_label)

        # required_snrA
        # Scatter plots of required SNR in the Teff / log(g) plane
        jobs.append("""
{python} scatter_plot_snr_required.py --label "Teff{{7000:3400}}" --label "logg{{5:0}}" \
  --label-axis-latex "Teff" --label-axis-latex "log(g)" \
  --label-axis-latex "{colour_label}" \
  --colour-by-label "{colour_label}" \
  --target-accuracy "{target_accuracy}" \
  --colour-range-min 30 --colour-range-max 120 \
  --cannon-output "{cannon_output}" \
  --accuracy-unit "{accuracy_unit}" \
  --output-stub "../../output_plots/cannon_performance/required_snrA/{cannon_run}/{path_safe_label}"
""".format(python=python_path, cannon_output=cannon_output, cannon_run=cannon_run, path_safe_label=path_safe_label,
           colour_label=colour_label, target_accuracy=target_accuracy, accuracy_unit=target_unit,
           data_path=workspace, out_path=os_path.join(output_path, "required_snrA")))

        # required_snrB
        # Scatter plots of required SNR in the metallicity / log(g) plane
        jobs.append("""
{python} scatter_plot_snr_required.py --label "[Fe/H]{{1:-3}}" --label "logg{{5:0}}" \
  --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
  --label-axis-latex "{colour_label}" \
  --colour-by-label "{colour_label}" \
  --target-accuracy "{target_accuracy}" \
  --colour-range-min 30 --colour-range-max 120 \
  --cannon-output "{cannon_output}" \
  --accuracy-unit "{accuracy_unit}" \
  --output-stub "{out_path}/{cannon_run}/{path_safe_label}"
""".format(python=python_path, cannon_output=cannon_output, cannon_run=cannon_run, path_safe_label=path_safe_label,
           colour_label=colour_label, target_accuracy=target_accuracy, accuracy_unit=target_unit,
           data_path=workspace, out_path=os_path.join(output_path, "required_snrB")))

        # label_offsets/A_*
        # Scatter plots of the absolute offsets in each label, in the Teff / log(g) plane
        jobs.append("""
{python} scatter_plot_coloured.py --label "Teff{{7000:3400}}" --label "logg{{5:0}}" \
  --label-axis-latex "Teff" --label-axis-latex "log(g)" \
  --label-axis-latex "{colour_label}" \
  --colour-by-label "{colour_label}{{:}}" \
  --colour-range-min "{axis_min}" \
  --colour-range-max "{axis_max}" \
  --cannon-output "{cannon_output}" \
  --output-stub "{out_path}/{cannon_run}/A_{path_safe_label}"
""".format(python=python_path, cannon_output=cannon_output, cannon_run=cannon_run, path_safe_label=path_safe_label,
           colour_label=colour_label, target_accuracy=target_accuracy, accuracy_unit=target_unit,
           axis_min=-3 * target_accuracy, axis_max=3 * target_accuracy,
           data_path=workspace, out_path=os_path.join(output_path, "label_offsets")))

        # label_offsets/B_*
        # Scatter plots of the absolute offsets in each label, in the [Fe/H] / log(g) plane
        jobs.append("""
{python} scatter_plot_coloured.py --label "[Fe/H]{{1:-3}}" --label "logg{{5:0}}" \
  --label-axis-latex "[Fe/H]" --label-axis-latex "log(g)" \
  --label-axis-latex "{colour_label}" \
  --colour-by-label "{colour_label}{{:}}" \
  --colour-range-min "{axis_min}" \
  --colour-range-max "{axis_max}" \
  --cannon-output "{cannon_output}" \
  --output-stub "{out_path}/{cannon_run}/B_{path_safe_label}"
""".format(python=python_path, cannon_output=cannon_output, cannon_run=cannon_run, path_safe_label=path_safe_label,
           colour_label=colour_label, target_accuracy=target_accuracy, accuracy_unit=target_unit,
           axis_min=-3 * target_accuracy, axis_max=3 * target_accuracy,
           data_path=workspace, out_path=os_path.join(output_path, "label_offsets")))

# Now run the shell commands
logger.info("Running {:d} shell commands".format(len(jobs)))
