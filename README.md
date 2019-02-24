The text on this page is a brief introduction to `4most-4gp-scripts`. For a
more complete tutorial, please visit the
[Wiki](https://github.com/dcf21/4most-4gp-scripts/wiki).

# About 4GP

4GP is the Galactic pipeline for the 4MOST multi-object
spectrograph, developed by Infrastructure Working Group 7 (IWG7).

The pipeline comprises a collection of Python modules which use a common
data format to store and manipulate spectra and their associated metadata. It
makes it easy to pass spectra between a range of spectral synthesis, processing and
analysis tools including Turbospectrum, the 4MOST Facility Simulator (4FS),
and abundance analysis codes such as the Cannon, without the need for manual data format conversion.

It includes
the ability to store spectra in libraries and search for them by arbitrary
metadata constraints, making it easy to create new tests on subgroups of stars
filtered from larger samples.

In addition, 4GP includes a simple web interface which allows the contents of spectrum libraries
to be searched and viewed quickly for diagnostic purposes.

### Code structure

The 4GP framework is available in two repositories on GitHub, and these Wiki pages provide
step-by-step installation instructions. The first repository contains the
Python modules which provide programmatic interfaces for creating and
manipulating libraries of spectra. It includes wrappers for passing them to
various analysis tools:

<https://github.com/dcf21/4most-4gp>

The second repository contains python scripts which utilise these modules to
create command-line tools for
synthesising spectra, manipulating them, and then testing abundance analysis codes such as the
Cannon and the Payne on them:

<https://github.com/dcf21/4most-4gp-scripts>

### Getting started

This code is under active development, but stable releases are periodically
made.

Visiting the GitHub URLs above will present you with the `master` branch of our
code, which should always correspond to the latest stable release. If you click
on the "branches" dropdown menu, you can select a different version of the code
to download.

Stable releases are given date stamps, for example, `release-2019-03-01-1`. The
master branch points to the most recent release. The `dev` branch may contain experimental code
and should be used with extreme caution.

# Installing 4most-4gp-scripts

Before installing the scripts in this repository, you must have installed the Python modules
contained in the [4most-4gp](https://github.com/dcf21/4most-4gp)
repository. If you have not already done this, you should read the associated
[wiki pages](https://github.com/dcf21/4most-4gp/wiki).

Once you have done this, you should check out the contents of this repository using the command:

```bash
git clone https://github.com/dcf21/4most-4gp-scripts.git
```

### Installation paths

When you install `4most-4gp-scripts`, many of the scripts need to be able to
locate tools such as Turbospectrum and 4FS which you installed as part of the
4GP installation process, and which they depend upon.

By far the simplest approach is if you install `4most-4gp-scripts` alongside
all the tools in the same directory where you keep your working copy of
`4most-4gp`. Thus, after installing various tools, this directory might look as
follows:

```bash
dcf21@astrolabe:~/iwg7_pipeline$ ls
4most-4gp                  downloads         idl_packages    rvspecfit
4most-4gp-scripts          forwardModelling  interpol_marcs  sme
4most-iwg7-pipeline-tests  fromBengt         OpSys           TheCannon
4MOST_testspectra          fromKeith         pepsi           turbospectrum-15.1
AnniesLasso                hot_stars         pyphot          virtualenv
```

This is the default place where 4GP looks to find each tool, and if they are
installed in this way then you will not need to explicitly tell it where to
look.

You are permitted to install these tools in a different location, but then you
will need to pass configuration parameters to a number of 4GP's modules
(usually called `binary_path`) to tell it where to find each tool.

