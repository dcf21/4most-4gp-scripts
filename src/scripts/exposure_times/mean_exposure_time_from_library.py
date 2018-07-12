#!../../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python mean_exposure_time_from_library.py>, but <./mean_exposure_time_from_library.py> will not work.

"""
Take a bunch of template spectra in a SpectrumLibrary, and list the exposure times needed to observe them if they
were at some particular reference magnitude.
"""

from os import path as os_path
import numpy as np
import argparse
import logging

from fourgp_speclib import SpectrumLibrarySqlite
from fourgp_fourfs import FourFS

our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "../../../..")

# Read input parameters
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--library',
                    required=True,
                    dest="library",
                    help="The name of the spectrum library we are to read input spectra from. A subset of the stars "
                         "in the input library may optionally be selected by suffixing its name with a comma-separated "
                         "list of constraints in [] brackets. Use the syntax my_library[Teff=3000] to demand equality, "
                         "or [0<[Fe/H]<0.2] to specify a range. We do not currently support other operators like "
                         "[Teff>5000], but such ranges are easy to recast is a range, e.g. [5000<Teff<9999].")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where 4FS package is installed.")
parser.add_argument('--snr-definition',
                    action="append",
                    dest="snr_definitions",
                    help="Specify a way of defining SNR, in the form 'name,minimum,maximum', meaning we calculate the "
                         "median SNR per pixel between minimum and maximum wavelengths in Angstrom.")
parser.add_argument('--snr-list',
                    required=False,
                    default="10,12,14,16,18,20,23,26,30,35,40,45,50,80,100,130,180,250",
                    dest="snr_list",
                    help="Specify a comma-separated list of the SNRs that 4FS is to degrade spectra to.")
parser.add_argument('--snr-definitions-lrs',
                    required=False,
                    default="",
                    dest="snr_definitions_lrs",
                    help="Specify the SNR definition to use for LRS. For example, 'GalDiskHR_536NM' to use the S4 "
                         "green definition of SNR. You can even specify three comma-separated definitions, e.g. "
                         "'GalDiskHR_536NM,GalDiskHR_536NM,GalDiskHR_536NM' to use different SNR metrics for the "
                         "RGB arms within 4MOST LRS, though this is a pretty weird thing to want to do.")
parser.add_argument('--snr-definitions-hrs',
                    required=False,
                    default="",
                    dest="snr_definitions_hrs",
                    help="Specify the SNR definition to use for HRS. For example, 'GalDiskHR_536NM' to use the S4 "
                         "green definition of SNR. You can even specify three comma-separated definitions, e.g. "
                         "'GalDiskHR_536NM,GalDiskHR_536NM,GalDiskHR_536NM' to use different SNR metrics for the "
                         "RGB arms within 4MOST HRS, though this is a pretty weird thing to want to do.")
parser.add_argument('--run-hrs',
                    action='store_true',
                    dest="run_hrs",
                    help="Set 4FS to produce output for 4MOST HRS [default].")
parser.add_argument('--no-run-hrs',
                    action='store_false',
                    dest="run_hrs",
                    help="Set 4FS not to produce output for 4MOST HRS. Setting this will make us run quicker.")
parser.set_defaults(run_hrs=True)
parser.add_argument('--run-lrs',
                    action='store_true',
                    dest="run_lrs",
                    help="Set 4FS to produce output for 4MOST LRS [default].")
parser.add_argument('--no-run-lrs',
                    action='store_false',
                    dest="run_lrs",
                    help="Set 4FS not to produce output for 4MOST LRS. Setting this will make us run quicker.")
parser.set_defaults(run_lrs=True)
parser.add_argument('--photometric-band',
                    required=False,
                    default="SDSS_r",
                    dest="photometric_band",
                    help="The name of the photometric band in which the magnitudes in --mag-list are specified. This "
                         "must match a band which is recognised by the pyphot python package.")
parser.add_argument('--mag-list',
                    required=False,
                    default="15",
                    dest="mag_list",
                    help="Specify a comma-separated list of the magnitudes to assume when simulating observations "
                         "of each object. If multiple magnitudes are specified, than each input spectrum we be "
                         "output multiple times, once at each magnitude.")
args = parser.parse_args()

# Start logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Calculating magnitudes and exposure times for templates")

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "../../../workspace")
os.system("mkdir -p {}".format(workspace))

# Parse any definitions of SNR we were supplied on the command line
if (args.snr_definitions is None) or (len(args.snr_definitions) < 1):
    snr_definitions = None
else:
    snr_definitions = []
    for snr_definition in args.snr_definitions:
        words = snr_definition.split(",")
        snr_definitions.append([words[0], float(words[1]), float(words[2])])

# Look up what definition of SNR is user specified we should use for 4MOST LRS
if len(args.snr_definitions_lrs) < 1:
    # Case 1: None was specified, so we use default
    snr_definitions_lrs = None
else:
    snr_definitions_lrs = args.snr_definitions_lrs.split(",")
    # Case 2: A single definition was supplied which we use for all three arms
    if len(snr_definitions_lrs) == 1:
        snr_definitions_lrs *= 3
    # Case 3: Three definitions were supplied, one for each arm
    assert len(snr_definitions_lrs) == 3

# Look up what definition of SNR is user specified we should use for 4MOST HRS
if len(args.snr_definitions_hrs) < 1:
    # Case 1: None was specified, so we use default
    snr_definitions_hrs = None
else:
    snr_definitions_hrs = args.snr_definitions_hrs.split(",")
    # Case 2: A single definition was supplied which we use for all three arms
    if len(snr_definitions_hrs) == 1:
        snr_definitions_hrs *= 3
    # Case 3: Three definitions were supplied, one for each arm
    assert len(snr_definitions_hrs) == 3

# Parse the list of SNRs that the user specified on the command line
snr_list = [float(item.strip()) for item in args.snr_list.split(",")]

# Parse the list of magnitudes that the user specified on the command line
mag_list = [float(item.strip()) for item in args.mag_list.split(",")]

# Initialise output data structure
output = {}  # output[magnitude]["HRS"][snr] = list of exposure times in seconds

# Loop over all the magnitudes we are to simulate for each object
for magnitude in mag_list:

    # Instantiate 4FS wrapper
    etc_wrapper = FourFS(
        path_to_4fs=os_path.join(args.binary_path, "OpSys/ETC"),
        snr_definitions=snr_definitions,
        magnitude=magnitude,
        magnitude_unreddened=False,
        photometric_band=args.photometric_band,
        run_lrs=args.run_lrs,
        run_hrs=args.run_hrs,
        lrs_use_snr_definitions=snr_definitions_lrs,
        hrs_use_snr_definitions=snr_definitions_hrs,
        snr_list=snr_list,
        snr_per_pixel=False
    )

    # Open input SpectrumLibrary, and search for flux normalised spectra meeting our filtering constraints
    spectra = SpectrumLibrarySqlite.open_and_search(library_spec=args.library,
                                                    workspace=workspace,
                                                    extra_constraints={"continuum_normalised": 0}
                                                    )

    # Get a list of the spectrum IDs which we were returned
    input_library, input_spectra_ids, input_spectra_constraints = [spectra[i]
                                                                   for i in ("library", "items", "constraints")]

    # Loop over spectra to process
    for input_spectrum_id in input_spectra_ids:
        logger.info("Working on <{}>".format(input_spectrum_id['filename']))

        # Open Spectrum data from disk
        input_spectrum_array = input_library.open(ids=input_spectrum_id['specId'])

        # Turn SpectrumArray object into a Spectrum object
        input_spectrum = input_spectrum_array.extract_item(0)

        # Look up the unique ID of the star we've just loaded
        # Newer spectrum libraries have a uid field which is guaranteed unique; for older spectrum libraries use
        # Starname instead.

        # Work out which field we're using (uid or Starname)
        spectrum_matching_field = 'uid' if 'uid' in input_spectrum.metadata else 'Starname'

        # Look up the unique ID of this object
        object_name = input_spectrum.metadata[spectrum_matching_field]

        # Search for the continuum-normalised version of this same object (which will share the same uid / name)
        search_criteria = input_spectra_constraints.copy()
        search_criteria[spectrum_matching_field] = object_name
        search_criteria['continuum_normalised'] = 1
        continuum_normalised_spectrum_id = input_library.search(**search_criteria)

        # Check that continuum-normalised spectrum exists and is unique
        assert len(continuum_normalised_spectrum_id) == 1, "Could not find continuum-normalised spectrum."

        # Load the continuum-normalised version
        input_spectrum_continuum_normalised_arr = input_library.open(
            ids=continuum_normalised_spectrum_id[0]['specId']
        )

        # Turn the SpectrumArray we got back into a single Spectrum
        input_spectrum_continuum_normalised = input_spectrum_continuum_normalised_arr.extract_item(0)

        # Pass this spectrum to 4FS
        degraded_spectra = etc_wrapper.process_spectra(
            spectra_list=((input_spectrum, input_spectrum_continuum_normalised),)
        )

        # Loop over LRS and HRS
        for mode in degraded_spectra:
            # Loop over the spectra we simulated (there was only one!)
            for index in degraded_spectra[mode]:
                # Loop over the various SNRs we simulated
                for snr in degraded_spectra[mode][index]:
                    # Extract the exposure time returned by 4FS from the metadata associated with this Spectrum object
                    # The exposure time is recorded in seconds
                    exposure_time = degraded_spectra[mode][index][snr]["spectrum"].metadata["exposure"]

                    # Record this exposure time into a list of the times recorded for this [mag][mode][snr] combination
                    if magnitude not in output:
                        output[magnitude] = {}
                    if mode not in output:
                        output[magnitude][mode] = {}
                    if snr not in output[mode]:
                        output[magnitude][mode][snr] = []
                    output[magnitude][mode][snr].append(exposure_time)

# Print output
for magnitude in sorted(output.keys()):
    for mode in sorted(output[magnitude].keys()):
        for snr in sorted(output[magnitude][mode].keys()):
            # Calculate the mean exposure time, and the standard deviation of the distribution
            exposure_time_mean = np.mean(output[mode][snr])
            exposure_time_sd = np.std(output[mode][snr])

            # Print a row of output
            print "{mode:6s} {magnitude:6.1f} {snr:6.1f} {mean:6.3f} {std_dev:6.3f}".format(mode=mode,
                                                                                            magnitude=magnitude,
                                                                                            snr=snr,
                                                                                            mean=exposure_time_mean,
                                                                                            std_dev=exposure_time_sd
                                                                                            )
