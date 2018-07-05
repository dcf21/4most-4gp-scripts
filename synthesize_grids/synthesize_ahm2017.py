#!../../../virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python synthesize_ahm2017.py>, but <./synthesize_ahm2017.py> will not work.

"""
Take parameters of GES sample of stars proposed by Georges at the AHM2017 in Lyon, and synthesize spectra using
TurboSpectrum.
"""

import numpy as np
import logging
import json
from astropy.io import fits
from lib.base_synthesizer import Synthesizer

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
synthesizer = Synthesizer(library_name="ahm2017_sample",
                          logger=logger,
                          docstring=__doc__)

# Table supplies list of abundances for GES stars
f = fits.open("../../downloads/GES_iDR5_WG15_Recommended.fits")
ges = f[1].data
ges_fields = ges.names
# print ges_fields  # To print a list of available parameters

"""
>>> print ges.names
['CNAME', 'GES_FLD', 'OBJECT', 'FILENAME', 'GES_TYPE', 'REC_SETUP', 'RAVAIL_SETUP', 'SETUP', 'REC_WG', 'RAVAIL_WG',
 'WG', 'RA', 'DEC', 'SNR', 'TEFF', 'E_TEFF', 'NN_TEFF', 'ENN_TEFF', 'NNE_TEFF', 'SYS_ERR_TEFF', 'LOGG', 'E_LOGG',
 'NN_LOGG', 'ENN_LOGG', 'NNE_LOGG', 'SYS_ERR_LOGG', 'LIM_LOGG', 'FEH', 'E_FEH', 'NN_FEH', 'ENN_FEH', 'NNE_FEH',
 'SYS_ERR_FEH', 'XI', 'E_XI', 'NN_XI', 'ENN_XI', 'NNE_XI', 'MH', 'E_MH', 'NN_MH', 'ENN_MH', 'NNE_MH', 'ALPHA_FE',
 'E_ALPHA_FE', 'NN_ALPHA_FE', 'ENN_ALPHA_FE', 'NNE_ALPHA_FE', 'VRAD', 'E_VRAD', 'PROV_VRAD', 'VRAD_OFFSET',
 'VRAD_FILENAME', 'VSINI', 'E_VSINI', 'LIM_VSINI', 'TEFF_PHOT', 'E_TEFF_PHOT', 'TEFF_IRFM', 'E_TEFF_IRFM', 'FBOL_IRFM',
 'HE1', 'UPPER_COMBINED_HE1', 'E_HE1', 'NN_HE1', 'ENN_HE1', 'NL_HE1', 'PROVENANCE_HE1', 'LI1', 'UPPER_COMBINED_LI1',
 'E_LI1', 'NN_LI1', 'ENN_LI1', 'NL_LI1', 'PROVENANCE_LI1', 'C1', 'UPPER_COMBINED_C1', 'E_C1', 'NN_C1', 'ENN_C1',
 'NL_C1', 'PROVENANCE_C1', 'C2', 'UPPER_C2', 'E_C2', 'NN_C2', 'ENN_C2', 'NL_C2', 'PROVENANCE_C2', 'C3', 'UPPER_C3',
 'E_C3', 'NN_C3', 'ENN_C3', 'NL_C3', 'PROVENANCE_C3', 'C_C2', 'UPPER_C_C2', 'E_C_C2', 'NN_C_C2', 'ENN_C_C2', 'NL_C_C2',
 'PROVENANCE_C_C2', 'N2', 'UPPER_N2', 'E_N2', 'NN_N2', 'ENN_N2', 'NL_N2', 'PROVENANCE_N2', 'N3', 'UPPER_N3', 'E_N3',
 'NN_N3', 'ENN_N3', 'NL_N3', 'PROVENANCE_N3', 'N_CN', 'UPPER_N_CN', 'E_N_CN', 'NN_N_CN', 'ENN_N_CN', 'NL_N_CN',
 'PROVENANCE_N_CN', 'O1', 'UPPER_COMBINED_O1', 'E_O1', 'NN_O1', 'ENN_O1', 'NL_O1', 'PROVENANCE_O1', 'O2', 'UPPER_O2',
 'E_O2', 'NN_O2', 'ENN_O2', 'NL_O2', 'PROVENANCE_O2', 'NE1', 'UPPER_COMBINED_NE1', 'E_NE1', 'NN_NE1', 'ENN_NE1',
 'NL_NE1', 'PROVENANCE_NE1', 'NE2', 'UPPER_NE2', 'E_NE2', 'NN_NE2', 'ENN_NE2', 'NL_NE2', 'NA1', 'UPPER_COMBINED_NA1',
 'E_NA1', 'NN_NA1', 'ENN_NA1', 'NL_NA1', 'PROVENANCE_NA1', 'MG1', 'UPPER_COMBINED_MG1', 'E_MG1', 'NN_MG1', 'ENN_MG1',
 'NL_MG1', 'PROVENANCE_MG1', 'MG2', 'UPPER_MG2', 'E_MG2', 'NN_MG2', 'ENN_MG2', 'NL_MG2', 'PROVENANCE_MG2', 'AL1',
 'UPPER_COMBINED_AL1', 'E_AL1', 'NN_AL1', 'ENN_AL1', 'NL_AL1', 'PROVENANCE_AL1', 'AL2', 'UPPER_AL2', 'E_AL2', 'NN_AL2',
 'ENN_AL2', 'NL_AL2', 'PROVENANCE_AL2', 'AL3', 'UPPER_AL3', 'E_AL3', 'NN_AL3', 'ENN_AL3', 'NL_AL3', 'SI1',
 'UPPER_COMBINED_SI1', 'E_SI1', 'NN_SI1', 'ENN_SI1', 'NL_SI1', 'PROVENANCE_SI1', 'SI2', 'UPPER_SI2', 'E_SI2', 'NN_SI2',
 'ENN_SI2', 'NL_SI2', 'PROVENANCE_SI2', 'SI3', 'UPPER_SI3', 'E_SI3', 'NN_SI3', 'ENN_SI3', 'NL_SI3', 'PROVENANCE_SI3',
 'SI4', 'UPPER_SI4', 'E_SI4', 'NN_SI4', 'ENN_SI4', 'NL_SI4', 'PROVENANCE_SI4', 'S1', 'UPPER_COMBINED_S1', 'E_S1',
 'NN_S1', 'ENN_S1', 'NL_S1', 'PROVENANCE_S1', 'S2', 'UPPER_S2', 'E_S2', 'NN_S2', 'ENN_S2', 'NL_S2', 'S3', 'UPPER_S3',
 'E_S3', 'NN_S3', 'ENN_S3', 'NL_S3', 'CA1', 'UPPER_COMBINED_CA1', 'E_CA1', 'NN_CA1', 'ENN_CA1', 'NL_CA1',
 'PROVENANCE_CA1', 'CA2', 'UPPER_CA2', 'E_CA2', 'NN_CA2', 'ENN_CA2', 'NL_CA2', 'PROVENANCE_CA2', 'SC1',
 'UPPER_COMBINED_SC1', 'E_SC1', 'NN_SC1', 'ENN_SC1', 'NL_SC1', 'PROVENANCE_SC1', 'SC2', 'UPPER_SC2', 'E_SC2', 'NN_SC2',
 'ENN_SC2', 'NL_SC2', 'PROVENANCE_SC2', 'TI1', 'UPPER_COMBINED_TI1', 'E_TI1', 'NN_TI1', 'ENN_TI1', 'NL_TI1',
 'PROVENANCE_TI1', 'TI2', 'UPPER_TI2', 'E_TI2', 'NN_TI2', 'ENN_TI2', 'NL_TI2', 'PROVENANCE_TI2', 'V1',
 'UPPER_COMBINED_V1', 'E_V1', 'NN_V1', 'ENN_V1', 'NL_V1', 'PROVENANCE_V1', 'V2', 'UPPER_V2', 'E_V2', 'NN_V2', 'ENN_V2',
 'NL_V2', 'CR1', 'UPPER_COMBINED_CR1', 'E_CR1', 'NN_CR1', 'ENN_CR1', 'NL_CR1', 'PROVENANCE_CR1', 'CR2', 'UPPER_CR2',
 'E_CR2', 'NN_CR2', 'ENN_CR2', 'NL_CR2', 'PROVENANCE_CR2', 'MN1', 'UPPER_COMBINED_MN1', 'E_MN1', 'NN_MN1', 'ENN_MN1',
 'NL_MN1', 'PROVENANCE_MN1', 'FE1', 'UPPER_COMBINED_FE1', 'E_FE1', 'NN_FE1', 'ENN_FE1', 'NL_FE1', 'PROVENANCE_FE1',
 'FE2', 'UPPER_FE2', 'E_FE2', 'NN_FE2', 'ENN_FE2', 'NL_FE2', 'PROVENANCE_FE2', 'FE3', 'UPPER_FE3', 'E_FE3', 'NN_FE3',
 'ENN_FE3', 'NL_FE3', 'CO1', 'UPPER_COMBINED_CO1', 'E_CO1', 'NN_CO1', 'ENN_CO1', 'NL_CO1', 'PROVENANCE_CO1', 'NI1',
 'UPPER_COMBINED_NI1', 'E_NI1', 'NN_NI1', 'ENN_NI1', 'NL_NI1', 'PROVENANCE_NI1', 'CU1', 'UPPER_COMBINED_CU1', 'E_CU1',
 'NN_CU1', 'ENN_CU1', 'NL_CU1', 'PROVENANCE_CU1', 'ZN1', 'UPPER_COMBINED_ZN1', 'E_ZN1', 'NN_ZN1', 'ENN_ZN1', 'NL_ZN1',
 'PROVENANCE_ZN1', 'SR1', 'UPPER_COMBINED_SR1', 'E_SR1', 'NN_SR1', 'ENN_SR1', 'NL_SR1', 'PROVENANCE_SR1', 'Y1',
 'UPPER_COMBINED_Y1', 'E_Y1', 'NN_Y1', 'ENN_Y1', 'NL_Y1', 'Y2', 'UPPER_Y2', 'E_Y2', 'NN_Y2', 'ENN_Y2', 'NL_Y2',
 'PROVENANCE_Y2', 'ZR1', 'UPPER_COMBINED_ZR1', 'E_ZR1', 'NN_ZR1', 'ENN_ZR1', 'NL_ZR1', 'PROVENANCE_ZR1', 'ZR2',
 'UPPER_ZR2', 'E_ZR2', 'NN_ZR2', 'ENN_ZR2', 'NL_ZR2', 'PROVENANCE_ZR2', 'NB1', 'UPPER_COMBINED_NB1', 'E_NB1', 'NN_NB1',
 'ENN_NB1', 'NL_NB1', 'MO1', 'UPPER_COMBINED_MO1', 'E_MO1', 'NN_MO1', 'ENN_MO1', 'NL_MO1', 'PROVENANCE_MO1', 'RU1',
 'UPPER_COMBINED_RU1', 'E_RU1', 'NN_RU1', 'ENN_RU1', 'NL_RU1', 'PROVENANCE_RU1', 'BA2', 'UPPER_BA2', 'E_BA2', 'NN_BA2',
 'ENN_BA2', 'NL_BA2', 'PROVENANCE_BA2', 'LA2', 'UPPER_LA2', 'E_LA2', 'NN_LA2', 'ENN_LA2', 'NL_LA2', 'PROVENANCE_LA2',
 'CE2', 'UPPER_CE2', 'E_CE2', 'NN_CE2', 'ENN_CE2', 'NL_CE2', 'PROVENANCE_CE2', 'PR2', 'UPPER_PR2', 'E_PR2', 'NN_PR2',
 'ENN_PR2', 'NL_PR2', 'PROVENANCE_PR2', 'ND2', 'UPPER_ND2', 'E_ND2', 'NN_ND2', 'ENN_ND2', 'NL_ND2', 'PROVENANCE_ND2',
 'SM2', 'UPPER_SM2', 'E_SM2', 'NN_SM2', 'ENN_SM2', 'NL_SM2', 'PROVENANCE_SM2', 'EU2', 'UPPER_EU2', 'E_EU2', 'NN_EU2',
 'ENN_EU2', 'NL_EU2', 'PROVENANCE_EU2', 'GD2', 'UPPER_GD2', 'E_GD2', 'NN_GD2', 'ENN_GD2', 'NL_GD2', 'DY2', 'UPPER_DY2',
 'E_DY2', 'NN_DY2', 'ENN_DY2', 'NL_DY2', 'SPT', 'VEIL', 'E_VEIL', 'EW_LI', 'LIM_EW_LI', 'E_EW_LI', 'PROVENANCE_EW_LI',
 'EWC_LI', 'LIM_EWC_LI', 'E_EWC_LI', 'EW_HA_ACC', 'E_EW_HA_ACC', 'HA10', 'E_HA10', 'EW_HA_CHR', 'E_EW_HA_CHR',
 'FHA_CHR', 'E_FHA_CHR', 'FWZI', 'E_FWZI', 'EW_HB_CHR', 'E_EW_HB_CHR', 'FHB_CHR', 'E_FHB_CHR', 'LOG_MDOT_ACC',
 'E_LOG_MDOT_ACC', 'LOG_L_ACC', 'E_LOG_L_ACC', 'GAMMA', 'E_GAMMA', 'CONVOL', 'E_CONVOL', 'M_ALPHA', 'M_GRID', 'M_BROAD',
 'M_LOOPS', 'M_NAME', 'PECULI', 'REMARK', 'TECH']
"""

# Obtain solar abundances, needed to convert values in file into solar units
sun_id = np.where(ges.OBJECT == 'Sun_Benchmarks_BordeauxLib3     ')[0]

# Filter objects as specified by Georges at Lyon meeting
selection = np.where(
    (ges.SNR > 20) & (ges.REC_WG == 'WG11') & (ges.E_FEH < 0.15) & (ges.E_VRAD < 10.) & (ges.E_TEFF < 100.) & (
            ges.E_LOGG < 0.2))[0]
stellar_data = ges[selection]

# Loop over stars extracting stellar parameters from FITS file
star_list = []
for star_index in range(len(stellar_data)):
    star_list_item = {
        "name": stellar_data.CNAME[star_index],
        "Teff": float(stellar_data.TEFF[star_index]),
        "[Fe/H]": float(stellar_data.FEH[star_index]),
        "logg": float(stellar_data.LOGG[star_index]),
        "extra_metadata": {
            "[alpha/Fe]": float(stellar_data.ALPHA_FE[star_index])
        },
        "free_abundances": {},
        "input_data": {}
    }

    # Pass list of the abundances of individual elements to TurboSpectrum
    free_abundances = star_list_item["free_abundances"]
    for elements, ionisation_state in ((element_list, 1), (element_list_ionised, 2)):
        for element in elements:
            if (not synthesizer.args.elements) or (element in synthesizer.args.elements.split(",")):
                fits_field_name = "{}{}".format(element.upper(), ionisation_state)

                # Normalise abundance of element to solar
                abundance = stellar_data[fits_field_name][star_index] - ges[fits_field_name][sun_id]

                if np.isfinite(abundance):
                    free_abundances[element] = float(abundance)

    # Propagate all ionisation states into metadata
    metadata = star_list_item["extra_metadata"]
    for element in element_list:
        abundances_all = []
        for ionisation_state in range(1, 5):
            fits_field_name = "{}{}".format(element.upper(), ionisation_state)
            if fits_field_name in ges_fields:
                abundance = stellar_data[fits_field_name][star_index] - ges[fits_field_name][sun_id]
                abundances_all.append(float(abundance))
            else:
                abundances_all.append(None)
        metadata["[{}/H]_ionised_states".format(element)] = json.dumps(abundances_all)

    # Propagate all input fields from the FITS file into <input_data>
    input_data = star_list_item["input_data"]
    for col_name in ges_fields:
        if col_name == "CNAME":
            continue
        value = stellar_data[col_name][star_index]

        if ges.dtype[col_name].type is np.string_:
            typed_value = str(value)
        else:
            typed_value = float(value)

        input_data[col_name] = typed_value
    star_list.append(star_list_item)

# Pass list of stars to synthesizer
synthesizer.set_star_list(star_list)

# Output data into sqlite3 db
synthesizer.dump_stellar_parameters_to_sqlite()

# Create new SpectrumLibrary
synthesizer.create_spectrum_library()

# Iterate over the spectra we're supposed to be synthesizing
synthesizer.do_synthesis()

# Close TurboSpectrum synthesizer instance
synthesizer.clean_up()
