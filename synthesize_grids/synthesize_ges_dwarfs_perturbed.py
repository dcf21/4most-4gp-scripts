#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take stellar parameters of GES dwarf stars and synthesize spectra using TurboSpectrum.
"""

import os
import re
import time
import hashlib
import argparse
import numpy as np
from os import path as os_path
import logging
import json
import random
from astropy.io import fits

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_telescope_data import FourMost
from fourgp_specsynth import TurboSpectrum

# List of elements whose abundances we pass to TurboSpectrum
# Elements with neutral abundances, e.g. LI1
element_list = (
    "He", "Li", "C", "O", "Ne", "Na", "Mg", "Al", "Si", "S", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Co", "Ni", "Cu", "Zn",
    "Sr", "Y", "Zr", "Nb", "Mo", "Ru")

# Elements with ionised abundances, e.g. N2
element_list_ionised = ("N", "Ba", "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Dy")


# Convenience function, coz it would've been too helpful for astropy to actually provide dictionary access to rows
def astropy_row_to_dict(x):
    return dict([(i, x[i]) for i in x.columns])


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing GES dwarf spectra")

# Read input parameters
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = os_path.join(our_path, "..", "..")
pid = os.getpid()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-library',
                    required=False,
                    default="turbospec_ges_dwarf_perturbed",
                    dest="library",
                    help="Specify the name of the SpectrumLibrary we are to feed synthesized spectra into.")
parser.add_argument('--workspace', dest='workspace', default="",
                    help="Directory where we expect to find spectrum libraries.")
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
                    default="/tmp/turbospec_ges_dwarf_perturbed_{}".format(pid),
                    dest="log_to",
                    help="Specify a log directory where we log our progress and configuration files.")
parser.add_argument('--star-list',
                    required=False,
                    default="../../downloads/GES_iDR5_WG15_Recommended.fits",
                    dest="star_list",
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

logger.info("Synthesizing perturbed GES dwarfs with arguments <{}> <{}>".format(args.library, args.star_list))

# Set path to workspace where we create libraries of spectra
workspace = args.workspace if args.workspace else os_path.join(our_path, "..", "workspace")
os.system("mkdir -p {}".format(workspace))

# Table supplies list of abundances for GES stars
f = fits.open(args.star_list)
ges = f[1].data
ges_fields = ges.names

# Obtain solar abundances, needed to convert values in file into solar units
sun_id = np.where(ges.OBJECT == 'Sun_Benchmarks_BordeauxLib3     ')[0]

# Filter objects on SNR
min_SNR = 50
selection = np.where((ges.SNR > min_SNR) & (ges.REC_WG == 'WG11') & (ges.LOGG > 3.5))[0]
star_list = ges[selection]

# Create bins to divide stars into
bins = []
for metallicity_bin in (
        (0, None),
        (-0.5, 0),
        (-1, -0.5),
        (None, -1)
):
    for stellar_type in [
        {"name": "everything"}
    ]:
        bin_constraints = {}
        if metallicity_bin[0] is not None:
            bin_constraints["feh_min"] = metallicity_bin[0]
        if metallicity_bin[1] is not None:
            bin_constraints["feh_max"] = metallicity_bin[1]

        bin_constraints.update(stellar_type)
        bins.append({
            "constraints": bin_constraints,
            "contents": []
        })

# Divide stars in bins
for star in range(len(star_list)):
    teff = star_list.TEFF[star]
    logg = star_list.LOGG[star]
    feh = star_list.FEH[star]
    for bin in bins:
        if (
                ("teff_min" not in bin["constraints"] or teff >= bin["constraints"]["teff_min"]) and
                ("teff_max" not in bin["constraints"] or teff < bin["constraints"]["teff_max"]) and
                ("logg_min" not in bin["constraints"] or logg >= bin["constraints"]["logg_min"]) and
                ("logg_max" not in bin["constraints"] or logg < bin["constraints"]["logg_max"]) and
                ("feh_min" not in bin["constraints"] or feh >= bin["constraints"]["feh_min"]) and
                ("feh_max" not in bin["constraints"] or feh < bin["constraints"]["feh_max"])
        ):
            bin["contents"].append(star)
            break

# Create new list of stars producing a few hundred perturbed versions from each bin
test_stars = []
test_stars_per_bin = 300
for bin in bins:
    if bin["contents"]:
        for i in range(test_stars_per_bin):
            random_star = random.choice(bin["contents"])
            test_star = {}
            test_stars.append(test_star)
            test_star["teff"] = star_list.TEFF[random_star] + random.gauss(0, 100)
            test_star["logg"] = star_list.LOGG[random_star] + random.gauss(0, 0.1)
            test_star["feh"] = star_list.FEH[random_star] + random.gauss(0, 0.1)

            free_abundances = {}
            test_star["free_abundances"] = free_abundances

            for elements, ionisation_state in ((element_list, 1), (element_list_ionised, 2)):
                for element in elements:
                    fits_field_name = "{}{}".format(element.upper(), ionisation_state)

                    # Normalise abundance of element to solar
                    abundance = star_list[fits_field_name][random_star] - ges[fits_field_name][sun_id]

                    if np.isfinite(abundance):
                        free_abundances[element] = float(abundance) + random.gauss(0, 0.1)

# print len(test_stars)
# print json.dumps(test_stars)

# import sys
# sys.exit(0)

# test_stars = json.loads(open("ges_dwarf_data.json").read())

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
counter_output = 0

# Start making log output
os.system("mkdir -p {}".format(args.log_to))
logfile = os.path.join(args.log_to, "synthesis.log")

# Iterate over the spectra we're supposed to be synthesizing
with open(logfile, "w") as result_log:
    for star in test_stars:
        star_name = "ges_dwarf_perturbed_{:08d}".format(counter_output)
        unique_id = hashlib.md5(os.urandom(32).encode("hex")).hexdigest()[:16]

        metadata = {
            "Starname": str(star_name),
            "uid": str(unique_id),
            "Teff": float(star["teff"]),
            "[Fe/H]": float(star["feh"]),
            "logg": float(star["logg"])
        }

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
                              t_eff=float(star["teff"]),
                              metallicity=float(star["feh"]),
                              log_g=float(star["logg"])
                              )

        # Pass list of the abundances of individual elements to TurboSpectrum
        free_abundances = star["free_abundances"]
        for item, value in free_abundances.iteritems():
            metadata["[{}/H]".format(item)] = value

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
            filename = star_name

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
