#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 100:00:00
#SBATCH --exclusive
#
# job name and output file names
#SBATCH -J redden_galah
#SBATCH -o stdout_redden_galah_%j.out
#SBATCH -e stderr_redden_galah_%j.out
cat $0

# Add the software packages which 4GP depends upon
module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

# Activate the conda python environment
source activate myenv

# Rsync the spectrum libraries that we're going to run through the reddening code onto a local
# disk on the worker node. This is necessary as aurora tends to go into
# spin-lock reading data from the astro3 disk.
cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/src/scripts/degrade_spectra/
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace
rsync -a ../../../workspace/galah_test_sample_turbospec ${TMPDIR}/workspace/
echo Rsync done: `date`
echo Running reddening script: `date`

# Now we actually run the reddening code
python2.7 redden_library.py --input-library galah_test_sample_turbospec \
                            --workspace "${TMPDIR}/workspace" \
                            --output-library galah_test_sample_reddened \

# Once the code is done, we rsync the results from local storage back onto a shared disk
echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/galah_test_sample_reddened ../../../workspace
echo Rsync done: `date`

