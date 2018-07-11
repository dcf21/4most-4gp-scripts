#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 48:00:00
#
# job name and output file names
#SBATCH -J 4fs_demo_stars
#SBATCH -o stdout_4fs_demo_stars_%j.out
#SBATCH -e stderr_4fs_demo_stars_%j.out
cat $0

# NOTE THAT THE 4FS EXPOSURE TIME CALCULATOR RUNS *HORRENDOUSLY* SLOWLY ON
# LUNARC. DO YOU REALLY WANT TO DO THIS? REALLY???

# Add the software packages which 4FS depends upon
module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

# Activate the conda python environment
source activate myenv

# Rsync the spectrum libraries that we're going to run through 4FS onto a local
# disk on the worker node. This is necessary as aurora tends to go into
# spin-lock reading data from the astro3 disk.
cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/src/scripts/degrade_spectra/
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace
rsync -a ../../../workspace/demo_stars ${TMPDIR}/workspace/
echo Rsync done: `date`
echo Running 4fs script: `date`

# Now we actually run 4FS
python2.7 degrade_library_with_4fs.py --input-library demo_stars \
                                      --workspace "${TMPDIR}/workspace" \
                                      --snr-list 50 \
                                      --output-library-lrs 4fs_demo_stars_test_lrs \
                                      --output-library-hrs 4fs_demo_stars_test_hrs

# Once 4FS is done, we rsync the results from local storage back onto a shared disk
echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/4fs_demo_stars_test_* ../../../workspace
echo Rsync done: `date`

