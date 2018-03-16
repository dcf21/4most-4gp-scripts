#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 160:00:00
#SBATCH --exclusive
#
# job name and output file names
#SBATCH -J 4fs_galah_test_reddened
#SBATCH -o stdout_4fs_galah_test_reddened_%j.out
#SBATCH -e stderr_4fs_galah_test_reddened_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/degrade_spectra/
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace
rsync -a ../workspace/galah_test_sample_reddened ${TMPDIR}/workspace/
echo Rsync done: `date`
echo Running 4fs script: `date`

python2.7 degrade_library_with_4fs.py --input-library galah_test_sample_reddened \
                                      --workspace "${TMPDIR}/workspace" \
                                      --snr-list 50 \
                                      --output-library-lrs galah_test_sample_reddened_4fs_lrs \
                                      --output-library-hrs galah_test_sample_reddened_4fs_hrs

echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/galah_test_sample_reddened_4fs_* ../workspace
echo Rsync done: `date`

