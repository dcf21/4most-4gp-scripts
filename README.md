# 4most-4gp-scripts

This repository contains a collection of scripts which test the performance of
the 4MOST 4GP toolkit, and provide examples in how the python modules should be
invoked.

The shell script `do_everything.sh` runs many of the scripts in order of
dependency, though will probably take several days to run everything.

It is simplest if you check out the `4most-4gp-scripts` repository into the
same directory as the `4most-4gp` repository, and all of the required software
packages, e.g. Turbospectrum and 4FS. If you do so, the script
`do_everything.sh` will run without modification.

If the paths are different from this configuration, some scripts will need to
be passed different commandline settings to tell them where to find the
software and data files they need.

All of the scripts create and/or expect to find spectra in libraries in a
directory called `workspace` inside the `4most-4gp-script` working copy.

## Index of scripts

An incomplete summary of some of scripts is as follows:

### import_grids

The scripts in this directory import grids of spectra used by Andy Casey and
Keith Hawkins in previous work.

**import_apokasc.py** - Import the APOKASC test and training sets of
synthetic spectra created by Keith Hawkins. This data set comprises 1232
training spectra, plus 7007 test spectra. The test spectra represent 1001 stars
degraded to 7 different SNRs using 4FS.

**import_brani.py** - Import the grid of template spectra used by Brani's RV
estimation code. This is a rectangular grid sampling _T<sub>eff</sub>_ between
4000K and 8250K at 250K intervals; [Fe/H] between 0.5 and 3.0 at intervals of
0.5; log(g) between 1.5 and 5.5 at intervals of 0.5.

## synthesize_grids

The scripts in this directory synthesize spectra using Turbospectrum:

**synthesize_test.py** - Synthesize around a dozen demo stars, including the
Sun and other stars with a wide range of _T<sub>eff</sub>_ between 3500K and
7000K.

**synthesize_apokasc.py** - Synthesize spectra representing the APOKASC sample
of test and training stars for the Cannon. In total, 1232 training stars and
1001 test stars are synthesized. The resulting spectra have a spectral
resolution of 50,000, which is about twice the maximum spectral resolution of
4MOST.

## degrade_spectra

The scripts in this directory degrade high-resolution spectra to the resolution
we expect 4MOST observations to have. It also inserts synthetic noise into
spectra with variable SNR. Currently this is implemented using 4FS.

**degrade_apokasc_with_4fs.py** - Degrade the APOKASC sample of stars and
create a new spectrum library containing the degraded spectra.

## test_rv_determination

The scripts in this directory test the performance of the module `fourgp_rv`.

**rv_test.py** - Take random synthetic spectra from the APOKASC library, and
apply random radial velocities to them. Then attempt to infer the RV that was
applied using `fourgp_rv`. Produces a data file of the real and estimated RV
values.

## test_cannon_degraded_spec

The scripts in this directory trains the Cannon on the APOKASC training set,
and then tests how well the Cannon can reproduce the stellar parameters of the
APOKASC test set based on noisy synthetic spectra produced with 4FS.

**cannon_test.py** - Train the Cannon on the spectra in one spectrum library,
and then use the trained Cannon to estimate the stellar parameters of all the
spectra in another spectrum library.  ### Testing the Cannon with low-res
spectra

## visualisation

Produce plots of the output of the scripts above.

# Contact details
This code is maintained by:

Dominic Ford  
Lund Observatory  
Box 43  
SE-221 00 Lund  
Sweden

