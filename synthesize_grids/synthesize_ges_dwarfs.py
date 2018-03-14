#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Take stellar parameters of GES dwarf stars and synthesize spectra using TurboSpectrum.
"""

import os
import time
import hashlib
import numpy as np
from os import path as os_path
import logging
import json
import sqlite3
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
logger.info("Synthesizing GES dwarf spectra")

# Instantiate base synthesizer
synthesizer = Synthesizer(library_name="ges_dwarf_sample",
                          logger=logger)

# Table supplies list of abundances for GES stars
f = fits.open("../../downloads/GES_iDR5_WG15_Recommended.fits")
ges = f[1].data
ges_fields = ges.names

# Obtain solar abundances, needed to convert values in file into solar units
sun_id = np.where(ges.OBJECT == 'Sun_Benchmarks_BordeauxLib3     ')[0]

# Filter objects on SNR
min_SNR = 50
selection = np.where((ges.SNR > min_SNR) & (ges.REC_WG == 'WG11') & (ges.LOGG > 3.5))[0]
star_list = ges[selection]

# Output data into sqlite3 db
if args.sqlite_out:
    os.system("rm -f {}".format(args.sqlite_out))
    conn = sqlite3.connect(args.sqlite_out)
    c = conn.cursor()
    columns = []
    for col_name in ges_fields:
        col_type = ges.dtype[col_name]
        columns.append("{} {}".format(col_name, "TEXT" if col_type.type is np.string_ else "REAL"))
    c.execute("CREATE TABLE stars (uid INTEGER PRIMARY KEY, {});".format(",".join(columns)))

    for i in range(len(star_list)):
        print "%5d / %5d" % (i, len(star_list))
        c.execute("INSERT INTO stars (CNAME) VALUES (?);", (star_list.CNAME[i],))
        for col_name in ges_fields:
            if col_name == "CNAME":
                continue
            arguments = (
                str(star_list[col_name][i]) if ges.dtype[col_name].type is np.string_ else float(
                    star_list[col_name][i]),
                star_list.CNAME[i]
            )
            c.execute("UPDATE stars SET %s=? WHERE CNAME=?;" % col_name, arguments)
    conn.commit()
    conn.close()

# Output data into sqlite3 db
synthesizer.dump_stellar_parameters_to_sqlite()

# Create new SpectrumLibrary
synthesizer.create_spectrum_library()

# Iterate over the spectra we're supposed to be synthesizing
with open(logfile, "w") as result_log:
    for star in range(len(star_list)):
        star_name = star_list.CNAME[star]
        unique_id = hashlib.md5(os.urandom(32).encode("hex")).hexdigest()[:16]

        metadata = {
            "Starname": str(star_name),
            "uid": str(unique_id),
            "Teff": float(star_list.TEFF[star]),
            "[Fe/H]": float(star_list.FEH[star]),
            "logg": float(star_list.LOGG[star]),
            "[alpha/Fe]": float(star_list.ALPHA_FE[star])
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
                              t_eff=float(star_list.TEFF[star]),
                              metallicity=float(star_list.FEH[star]),
                              log_g=float(star_list.LOGG[star])
                              )

        # Pass list of the abundances of individual elements to TurboSpectrum
        free_abundances = {}
        for elements, ionisation_state in ((element_list, 1), (element_list_ionised, 2)):
            for element in elements:
                fits_field_name = "{}{}".format(element.upper(), ionisation_state)

                # Normalise abundance of element to solar
                abundance = star_list[fits_field_name][star] - ges[fits_field_name][sun_id]

                if np.isfinite(abundance):
                    free_abundances[element] = float(abundance)
                    metadata["[{}/H]".format(element)] = float(abundance)

        # Propagate all ionisation states into metadata
        for element in element_list:
            abundances_all = []
            for ionisation_state in range(1, 5):
                fits_field_name = "{}{}".format(element.upper(), ionisation_state)
                if fits_field_name in ges_fields:
                    abundance = star_list[fits_field_name][star] - ges[fits_field_name][sun_id]
                    abundances_all.append(float(abundance))
                else:
                    abundances_all.append(None)
            metadata["[{}/H]_ionised_states".format(element)] = json.dumps(abundances_all)

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
