#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take parameters of GALAH sample of stars proposed by Georges on 30 Oct 2017, and synthesize spectra using
TurboSpectrum.
"""

import os
import re
import time
import argparse
import numpy as np
from os import path as os_path
import logging
import json
import sqlite3
from astropy.io import fits

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_telescope_data import FourMost
from fourgp_specsynth import TurboSpectrum

# List of elements whose abundances we pass to TurboSpectrum
element_list = (
    'Al', 'Ba', 'C', 'Ca', 'Ce', 'Co', 'Cr', 'Cu', 'Eu', 'K', 'La', 'Li', 'Mg', 'Mn', 'Mo', 'Na', 'Nd', 'Ni', 'O',
    'Rb', 'Ru', 'Sc', 'Si', 'Sm', 'Sr', 'Ti', 'V', 'Y', 'Zn', 'Zr'
)


# Convenience function, coz it would've been too helpful for astropy to actually provide dictionary access to rows
def astropy_row_to_dict(x):
    return dict([(i, x[i]) for i in x.columns])


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing GALAH sample spectra")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-library',
                    required=False,
                    default="turbospec_galah_sample",
                    dest="library",
                    help="Specify the name of the SpectrumLibrary we are to feed synthesized spectra into.")
parser.add_argument('--create',
                    required=False,
                    action='store_true',
                    dest="create",
                    help="Create a clean SpectrumLibrary to feed synthesized spectra into")
parser.add_argument('--no-create',
                    required=False,
                    action='store_false',
                    dest="create",
                    help="Do not create a clean SpectrumLibrary to feed synthesized spectra into")
parser.set_defaults(create=True)
parser.add_argument('--log-dir',
                    required=False,
                    default="/tmp/turbospec_galah_{}".format(pid),
                    dest="log_to",
                    help="Specify a log directory where we log our progress and configuration files.")
parser.add_argument('--dump-to-sqlite-file',
                    required=False,
                    default="",
                    dest="sqlite_out",
                    help="Specify an sqlite3 filename where we dump the stellar parameters of the stars.")
parser.add_argument('--star-list',
                    required=False,
                    default="../../downloads/GALAH_trainingset_4MOST_errors.fits",
                    dest="galah_stars",
                    help="Specify an ASCII table which lists the stellar parameters of the stars to be synthesized.")
parser.add_argument('--line-lists-dir',
                    required=False,
                    default=root_path,
                    dest="lines_dir",
                    help="Specify a directory where line lists for TurboSpectrum can be found.")
parser.add_argument('--binary-path',
                    required=False,
                    default=root_path,
                    dest="binary_path",
                    help="Specify a directory where Turbospectrum and Interpol packages are installed.")
parser.add_argument('--every',
                    required=False,
                    default=1,
                    type=int,
                    dest="every",
                    help="Only process every nth spectrum. "
                         "This is useful when parallelising this script across multiple processes.")
parser.add_argument('--skip',
                    required=False,
                    default=0,
                    type=int,
                    dest="skip",
                    help="Skip n spectra before starting to process every nth. "
                         "This is useful when parallelising this script across multiple processes.")
parser.add_argument('--limit',
                    required=False,
                    default=0,
                    type=int,
                    dest="limit",
                    help="Only process a maximum of n spectra.")
args = parser.parse_args()

logger.info("Synthesizing GALAH sample with arguments <{}> <{}>".format(args.library, args.galah_stars))

# Set path to workspace where we create libraries of spectra
workspace = os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Table supplies list of abundances for GES stars
f = fits.open(args.galah_stars)
galah_stars = f[1].data
galah_fields = galah_stars.names
# print galah_fields  # To print a list of available parameters

"""
>>> print galah_fields
['SNR', 'Teff_sme', 'e_Teff_sme', 'Logg_sme', 'e_Logg_sme', 'Feh_sme', 'e_Feh_sme', 'Vmic_sme', 'e_Vmic_sme',
 'Vsini_sme', 'e_Vsini_sme', 'Ak', 'Alpha_fe_sme', 'e_Alpha_fe_sme', 'Al_abund_sme', 'e_Al_abund_sme',
 'flag_Al_abund_sme', 'Ba_abund_sme', 'e_Ba_abund_sme', 'flag_Ba_abund_sme', 'C_abund_sme', 'e_C_abund_sme',
 'flag_C_abund_sme', 'Ca_abund_sme', 'e_Ca_abund_sme', 'flag_Ca_abund_sme', 'Ce_abund_sme', 'e_Ce_abund_sme',
 'flag_Ce_abund_sme', 'Co_abund_sme', 'e_Co_abund_sme', 'flag_Co_abund_sme', 'Cr_abund_sme', 'e_Cr_abund_sme',
 'flag_Cr_abund_sme', 'Cu_abund_sme', 'e_Cu_abund_sme', 'flag_Cu_abund_sme', 'Eu_abund_sme', 'e_Eu_abund_sme',
 'flag_Eu_abund_sme', 'K_abund_sme', 'e_K_abund_sme', 'flag_K_abund_sme', 'La_abund_sme', 'e_La_abund_sme',
 'flag_La_abund_sme', 'Li_abund_sme', 'e_Li_abund_sme', 'flag_Li_abund_sme', 'Mg_abund_sme', 'e_Mg_abund_sme',
 'flag_Mg_abund_sme', 'Mn_abund_sme', 'e_Mn_abund_sme', 'flag_Mn_abund_sme', 'Mo_abund_sme', 'e_Mo_abund_sme',
 'flag_Mo_abund_sme', 'Na_abund_sme', 'e_Na_abund_sme', 'flag_Na_abund_sme', 'Nd_abund_sme', 'e_Nd_abund_sme',
 'flag_Nd_abund_sme', 'Ni_abund_sme', 'e_Ni_abund_sme', 'flag_Ni_abund_sme', 'O_abund_sme', 'e_O_abund_sme',
 'flag_O_abund_sme', 'Rb_abund_sme', 'e_Rb_abund_sme', 'flag_Rb_abund_sme', 'Ru_abund_sme', 'e_Ru_abund_sme',
 'flag_Ru_abund_sme', 'Sc_abund_sme', 'e_Sc_abund_sme', 'flag_Sc_abund_sme', 'Si_abund_sme', 'e_Si_abund_sme',
 'flag_Si_abund_sme', 'Sm_abund_sme', 'e_Sm_abund_sme', 'flag_Sm_abund_sme', 'Sr_abund_sme', 'e_Sr_abund_sme',
 'flag_Sr_abund_sme', 'Ti_abund_sme', 'e_Ti_abund_sme', 'flag_Ti_abund_sme', 'V_abund_sme', 'e_V_abund_sme',
 'flag_V_abund_sme', 'Y_abund_sme', 'e_Y_abund_sme', 'flag_Y_abund_sme', 'Zn_abund_sme', 'e_Zn_abund_sme',
 'flag_Zn_abund_sme', 'Zr_abund_sme', 'e_Zr_abund_sme', 'flag_Zr_abund_sme']
"""

# Output data into sqlite3 db
if args.sqlite_out:
    os.system("rm -f {}".format(args.sqlite_out))
    conn = sqlite3.connect(args.sqlite_out)
    c = conn.cursor()
    columns = []
    for col_name in galah_fields:
        col_type = galah_stars.dtype[col_name]
        columns.append("{} {}".format(col_name, "TEXT" if col_type.type is np.string_ else "REAL"))
    c.execute(
        "CREATE TABLE stars (uid INTEGER PRIMARY KEY, name VARCHAR(32) UNIQUE NOT NULL, {});".format(",".join(columns)))

    for i in range(len(galah_stars)):
        star_name = "star_{:08d}".format(i)
        print "%5d / %5d" % (i, len(galah_stars))
        c.execute("INSERT INTO stars (name) VALUES (?);", (star_name,))
        for col_name in galah_fields:
            arguments = (
                str(galah_stars[col_name][i]) if galah_stars.dtype[col_name].type is np.string_ else float(
                    galah_stars[col_name][i]),
                star_name
            )
            c.execute("UPDATE stars SET %s=? WHERE name=?;" % col_name, arguments)
    conn.commit()
    conn.close()

# Iterate over the spectra we're supposed to be synthesizing
star_list = []
for star in range(len(galah_stars)):
    star_name = "star_{:08d}".format(star)

    metadata = {
        "Starname": str(star_name),
        "Teff": float(galah_stars.Teff_sme[star]),
        "[Fe/H]": float(galah_stars.Feh_sme[star]),
        "logg": float(galah_stars.Logg_sme[star])
    }

    # Pass list of the abundances of individual elements to TurboSpectrum
    free_abundances = {}
    for element in element_list:
        fits_field_name = "{}_abund_sme".format(element)

        # Normalise abundance of element to solar
        abundance = galah_stars[fits_field_name][star]

        if np.isfinite(abundance):
            free_abundances[element] = float(abundance)
            metadata["[{}/H]".format(element)] = float(abundance)
    star_list.append([metadata, free_abundances])

# import json
# print json.dumps(star_list)
# import sys
# sys.exit(0)

# star_list = json.loads(open("synthesize_galah_data.json").read())

# Create new SpectrumLibrary
library_name = re.sub("/", "_", args.library)
library_path = os_path.join(workspace, library_name)
library = SpectrumLibrarySqlite(path=library_path, create=args.create)

# Invoke FourMost data class. Ensure that the spectra we produce are much higher resolution than 4MOST.
# We down-sample them later to whatever resolution we actually want.
FourMostData = FourMost()
lambda_min = FourMostData.bands["LRS"]["lambda_min"]
lambda_max = FourMostData.bands["LRS"]["lambda_max"]
line_lists_path = FourMostData.bands["LRS"]["line_lists_edvardsson"]
spectral_resolution = 50000

# Invoke a TurboSpectrum synthesizer instance
synthesizer = TurboSpectrum(
    turbospec_path=os_path.join(args.binary_path, "turbospectrum-15.1/exec-gf-v15.1"),
    interpol_path=os_path.join(args.binary_path, "interpol_marcs"),
    line_list_paths=[os_path.join(args.lines_dir, line_lists_path)],
    marcs_grid_path=os_path.join(args.binary_path, "fromBengt/marcs_grid"))

# Start making log output
os.system("mkdir -p {}".format(args.log_to))
logfile = os.path.join(args.log_to, "synthesis.log")

# Iterate over the spectra we're supposed to be synthesizing
counter_output = 0
with open(logfile, "w") as result_log:
    for (metadata, free_abundances) in star_list:
        star_name = metadata["Starname"]

        # User can specify that we should only do every nth spectrum, if we're running in parallel
        counter_output += 1
        if (args.limit > 0) and (counter_output > args.limit):
            break
        if (counter_output - args.skip) % args.every != 0:
            continue

        # Configure Turbospectrum with the stellar parameters of the next star
        synthesizer.configure(lambda_min=lambda_min,
                              lambda_max=lambda_max,
                              lambda_delta=float(lambda_min) / spectral_resolution,
                              line_list_paths=[os_path.join(args.lines_dir, line_lists_path)],
                              stellar_mass=1,
                              t_eff=float(metadata["Teff"]),
                              metallicity=float(metadata["[Fe/H]"]),
                              log_g=float(metadata["logg"])
                              )

        # Set free abundances
        synthesizer.configure(free_abundances=free_abundances)

        # Make spectrum
        time_start = time.time()
        turbospectrum_out = synthesizer.synthesise()
        time_end = time.time()

        # Log synthesizer status
        logfile_this = os.path.join(args.log_to, "{}.log".format(star_name))
        open(logfile_this, "w").write(json.dumps(turbospectrum_out))

        # Check for errors
        errors = turbospectrum_out['errors']
        if errors:
            result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                star_name, errors))
            result_log.flush()
            continue

        # Fetch filename of the spectrum we just generated
        filepath = os_path.join(turbospectrum_out["output_file"])

        # Insert spectrum into SpectrumLibrary
        try:
            filename = "spectrum_{:08d}".format(counter_output)

            # First import continuum-normalised spectrum, which is in columns 1 and 2
            metadata['continuum_normalised'] = 1
            spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 1), binary=False)
            library.insert(spectra=spectrum, filenames=filename)

            # Then import version with continuum, which is in columns 1 and 3
            metadata['continuum_normalised'] = 0
            spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 2), binary=False)
            library.insert(spectra=spectrum, filenames=filename)
        except (ValueError, IndexError):
            result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                star_name, "Could not read bsyn output"))
            result_log.flush()
            continue

        # Update log file to show our progress
        result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                            star_name, "OK"))
        result_log.flush()

# Close TurboSpectrum synthesizer instance
synthesizer.close()
