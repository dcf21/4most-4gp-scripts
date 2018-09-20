# -*- coding: utf-8 -*-

"""
Framework for code to synthesise a library of spectra.
"""

import os
import re
import time
import hashlib
import argparse
import numpy as np
from os import path as os_path
import json
import sqlite3

from fourgp_speclib import SpectrumLibrarySqlite, Spectrum
from fourgp_telescope_data import FourMost
from fourgp_specsynth import TurboSpectrum


class Synthesizer:

    # Convenience function to provide dictionary access to rows of an astropy table
    @staticmethod
    def astropy_row_to_dict(x):
        return dict([(i, x[i]) for i in x.columns])

    # Read input parameters
    def __init__(self, library_name, logger, docstring, root_path="../..", spectral_resolution=50000):
        self.logger = logger
        self.our_path = os_path.split(os_path.abspath(__file__))[0]
        self.root_path = os_path.join(self.our_path, root_path, "..")
        self.pid = os.getpid()
        self.spectral_resolution = spectral_resolution
        parser = argparse.ArgumentParser(description=docstring)
        parser.add_argument('--output-library',
                            required=False,
                            default="turbospec_{}".format(library_name),
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
                            default="/tmp/turbospec_{}_{}".format(library_name, self.pid),
                            dest="log_to",
                            help="Specify a log directory where we log our progress and configuration files.")
        parser.add_argument('--dump-to-sqlite-file',
                            required=False,
                            default="",
                            dest="sqlite_out",
                            help="Specify an sqlite3 filename where we dump the stellar parameters of the stars.")
        parser.add_argument('--line-lists-dir',
                            required=False,
                            default=self.root_path,
                            dest="lines_dir",
                            help="Specify a directory where line lists for TurboSpectrum can be found.")
        parser.add_argument('--elements',
                            required=False,
                            default="",
                            dest="elements",
                            help="Only read the abundances of a comma-separated list of elements, and use scaled-solar "
                                 "abundances for everything else.")
        parser.add_argument('--binary-path',
                            required=False,
                            default=self.root_path,
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
        self.args = parser.parse_args()

        self.logger.info("Synthesizing {} to <{}>".format(library_name, self.args.library))

        # Set path to workspace where we create libraries of spectra
        self.workspace = (self.args.workspace if self.args.workspace else
                          os_path.join(self.our_path, root_path, "workspace"))
        os.system("mkdir -p {}".format(self.workspace))

    def set_star_list(self, star_list):
        self.star_list = star_list

        # Ensure that every star has a name; number stars of not
        for i, item in enumerate(self.star_list):
            if 'name' not in item:
                item['name'] = "star_{:08d}".format(i)

        # Ensure that every star has free_abundances and extra metadata
        for i, item in enumerate(self.star_list):
            if 'free_abundances' not in item:
                item['free_abundances'] = {}
            if 'extra_metadata' not in item:
                item['extra_metadata'] = {}
            if 'microturbulence' not in item:
                item['microturbulence'] = 1

        # Ensure that we have a table of input data to dump to SQLite, if requested
        for item in self.star_list:
            if 'input_data' not in item:
                item['input_data'] = {'name': item['name'],
                                      'Teff': item['Teff'],
                                      '[Fe/H]': item['[Fe/H]'],
                                      'logg': item['logg']}
                item['input_data'].update(item['free_abundances'])
                item['input_data'].update(item['extra_metadata'])
            if 'name' not in item['input_data']:
                item['input_data']['name'] = item['name']

    def dump_stellar_parameters_to_sqlite(self):
        # Output data into sqlite3 db
        if self.args.sqlite_out:
            os.system("rm -f {}".format(self.args.sqlite_out))
            conn = sqlite3.connect(self.args.sqlite_out)
            c = conn.cursor()

            columns = []
            for col_name, col_value in self.star_list[0]['input_data'].iteritems():
                col_type_str = isinstance(col_value, basestring)
                columns.append("{} {}".format(col_name, "TEXT" if col_type_str else "REAL"))
            c.execute("CREATE TABLE stars (uid INTEGER PRIMARY KEY, {});".format(",".join(columns)))

            for i, item in enumerate(self.star_list):
                print "Writing sqlite parameter dump: %5d / %5d" % (i, len(self.star_list))
                c.execute("INSERT INTO stars (name) VALUES (?);", (item['input_data']['name'],))
                uid = c.lastrowid
                for col_name in item['input_data']:
                    if col_name == "name":
                        continue
                    arguments = (
                        str(item['input_data'][col_name]) if isinstance(item['input_data'][col_name], basestring)
                        else float(item['input_data'][col_name]),
                        uid
                    )
                    c.execute("UPDATE stars SET %s=? WHERE uid=?;" % col_name, arguments)
            conn.commit()
            conn.close()

    def create_spectrum_library(self):
        # Create new SpectrumLibrary
        self.library_name = re.sub("/", "_", self.args.library)
        self.library_path = os_path.join(self.workspace, self.library_name)
        self.library = SpectrumLibrarySqlite(path=self.library_path, create=self.args.create)

        # Invoke FourMost data class. Ensure that the spectra we produce are much higher resolution than 4MOST.
        # We down-sample them later to whatever resolution we actually want.
        self.FourMostData = FourMost()
        self.lambda_min = self.FourMostData.bands["LRS"]["lambda_min"]
        self.lambda_max = self.FourMostData.bands["LRS"]["lambda_max"]
        self.line_lists_path = self.FourMostData.bands["LRS"]["line_lists_edvardsson"]

        # Invoke a TurboSpectrum synthesizer instance
        self.synthesizer = TurboSpectrum(
            turbospec_path=os_path.join(self.args.binary_path, "turbospectrum-15.1/exec-gf-v15.1"),
            interpol_path=os_path.join(self.args.binary_path, "interpol_marcs"),
            line_list_paths=[os_path.join(self.args.lines_dir, self.line_lists_path)],
            marcs_grid_path=os_path.join(self.args.binary_path, "fromBengt/marcs_grid"))

        self.synthesizer.configure(lambda_min=self.lambda_min,
                                   lambda_max=self.lambda_max,
                                   lambda_delta=float(self.lambda_min) / self.spectral_resolution,
                                   line_list_paths=[os_path.join(self.args.lines_dir, self.line_lists_path)],
                                   stellar_mass=1)
        self.counter_output = 0

        # Start making log output
        os.system("mkdir -p {}".format(self.args.log_to))
        self.logfile = os.path.join(self.args.log_to, "synthesis.log")

    def do_synthesis(self):
        # Iterate over the spectra we're supposed to be synthesizing
        with open(self.logfile, "w") as result_log:
            for star in self.star_list:
                star_name = star['name']
                unique_id = hashlib.md5(os.urandom(32).encode("hex")).hexdigest()[:16]

                metadata = {
                    "Starname": str(star_name),
                    "uid": str(unique_id),
                    "Teff": float(star['Teff']),
                    "[Fe/H]": float(star['[Fe/H]']),
                    "logg": float(star['logg']),
                    "microturbulence": float(star["microturbulence"])
                }

                # User can specify that we should only do every nth spectrum, if we're running in parallel
                self.counter_output += 1
                if (self.args.limit > 0) and (self.counter_output > self.args.limit):
                    break
                if (self.counter_output - self.args.skip) % self.args.every != 0:
                    continue

                # Pass list of the abundances of individual elements to TurboSpectrum
                free_abundances = dict(star['free_abundances'])
                for element, abundance in free_abundances.iteritems():
                    metadata["[{}/H]".format(element)] = float(abundance)

                # Propagate all ionisation states into metadata
                metadata.update(star['extra_metadata'])

                # Configure Turbospectrum with the stellar parameters of the next star
                self.synthesizer.configure(
                    t_eff=float(star['Teff']),
                    metallicity=float(star['[Fe/H]']),
                    log_g=float(star['logg']),
                    stellar_mass=1 if "stellar_mass" not in star else star["stellar_mass"],
                    turbulent_velocity=1 if "microturbulence" not in star else star["microturbulence"],
                    free_abundances=free_abundances
                )

                # Make spectrum
                time_start = time.time()
                turbospectrum_out = self.synthesizer.synthesise()
                time_end = time.time()

                # Log synthesizer status
                logfile_this = os.path.join(self.args.log_to, "{}.log".format(star_name))
                open(logfile_this, "w").write(json.dumps(turbospectrum_out))

                # Check for errors
                errors = turbospectrum_out['errors']
                if errors:
                    result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(),
                                                                        time_end - time_start,
                                                                        star_name,
                                                                        errors))
                    result_log.flush()
                    continue

                # Fetch filename of the spectrum we just generated
                filepath = os_path.join(turbospectrum_out["output_file"])

                # Insert spectrum into SpectrumLibrary
                try:
                    filename = "spectrum_{:08d}".format(self.counter_output)

                    # First import continuum-normalised spectrum, which is in columns 1 and 2
                    metadata['continuum_normalised'] = 1
                    spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 1), binary=False)
                    self.library.insert(spectra=spectrum, filenames=filename)

                    # Then import version with continuum, which is in columns 1 and 3
                    metadata['continuum_normalised'] = 0
                    spectrum = Spectrum.from_file(filename=filepath, metadata=metadata, columns=(0, 2), binary=False)
                    self.library.insert(spectra=spectrum, filenames=filename)
                except (ValueError, IndexError):
                    result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                        star_name, "Could not read bsyn output"))
                    result_log.flush()
                    continue

                # Update log file to show our progress
                result_log.write("[{}] {:6.0f} sec {}: {}\n".format(time.asctime(), time_end - time_start,
                                                                    star_name, "OK"))
                result_log.flush()

    def clean_up(self):
        self.logger.info("Synthesized {:d} spectra.".format(self.counter_output))
        # Close TurboSpectrum synthesizer instance
        self.synthesizer.close()
