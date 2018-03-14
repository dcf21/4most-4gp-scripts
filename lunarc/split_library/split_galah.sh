#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 24:00:00
#
# job name and output file names
#SBATCH -J split_galah
#SBATCH -o stdout_split_galah_%j.out
#SBATCH -e stderr_split_galah_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/rearrange_libraries
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace
rsync -a ../workspace/turbospec_galah ${TMPDIR}/workspace/
echo Rsync done: `date`
echo Running split_galah script: `date`

python2.7 rearrange.py --input-library turbospec_galah \
                       --workspace "${TMPDIR}/workspace" \
                       --output-library galah_training_sample_turbospec \
                       --output-library galah_test_sample_turbospec \
                       --output-fraction 0.25 --output-fraction 0.75

echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/galah_*_sample_turbospec ../workspace
echo Rsync done: `date`
