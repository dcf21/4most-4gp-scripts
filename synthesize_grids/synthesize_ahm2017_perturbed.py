#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take parameters of GES sample of stars proposed by Georges at the AHM2017 in Lyon, and synthesize spectra using
TurboSpectrum.
"""

import os
import time
import hashlib
import numpy as np
from os import path as os_path
import logging
import json
import random
from astropy.io import fits

from fourgp_speclib import Spectrum
from base_synthesizer import Synthesizer

# List of elements whose abundances we pass to TurboSpectrum
# Elements with neutral abundances, e.g. LI1
element_list = (
    "He", "Li", "C", "O", "Ne", "Na", "Mg", "Al", "Si", "S", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Co", "Ni", "Cu", "Zn",
    "Sr", "Y", "Zr", "Nb", "Mo", "Ru")

# Elements with ionised abundances, e.g. N2
element_list_ionised = ("N", "Ba", "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Dy")

# Start logging our progress
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.info("Synthesizing AHM2017 spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="ahm2017_perturbed",
                          logger=logger)

# Table supplies list of abundances for GES stars
f = fits.open("../../downloads/GES_iDR5_WG15_Recommended.fits")
ges = f[1].data
ges_fields = ges.names

# Obtain solar abundances, needed to convert values in file into solar units
sun_id = np.where(ges.OBJECT == 'Sun_Benchmarks_BordeauxLib3     ')[0]

# Filter objects as specified by Georges at Lyon meeting
selection = np.where(
    (ges.SNR > 20) & (ges.REC_WG == 'WG11') & (ges.E_FEH < 0.15) & (ges.E_VRAD < 10.) & (ges.E_TEFF < 100.) & (
        ges.E_LOGG < 0.2))[0]
star_list = ges[selection]

# Create bins to divide stars into
bins = []
for metallicity_bin in (
        (0, None),
        (-0.5, 0),
        (-1, -0.5),
        (None, -1)
):
    for stellar_type in (
            {"teff_min": 4000, "teff_max": 6000, "logg_min": 3.5},
            {"teff_min": 6000, "logg_min": 3},
            {"name": "giants", "logg_max": 3},
            {"name": "misfits"}
    ):
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
                    if args.elements and (element in args.elements.split(",")):
                        fits_field_name = "{}{}".format(element.upper(), ionisation_state)

                        # Normalise abundance of element to solar
                        abundance = star_list[fits_field_name][random_star] - ges[fits_field_name][sun_id]

                        if np.isfinite(abundance):
                            free_abundances[element] = float(abundance) + random.gauss(0, 0.1)

# import json
# print json.dumps(test_stars)
# import sys
# sys.exit(0)

# test_stars = json.loads(open("ahm2017_data.json").read())

# Output data into sqlite3 db
synthesizer.dump_stellar_parameters_to_sqlite()

# Create new SpectrumLibrary
synthesizer.create_spectrum_library()

# Iterate over the spectra we're supposed to be synthesizing
with open(logfile, "w") as result_log:
    for star in test_stars:
        star_name = "ahm2017_perturbed_{:08d}".format(counter_output)
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
