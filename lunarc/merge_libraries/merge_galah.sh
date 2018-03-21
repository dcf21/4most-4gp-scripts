#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 48:00:00
#
# job name and output file names
#SBATCH -J merge_galah
#SBATCH -o stdout_4fs_merge_galah_%j.out
#SBATCH -e stderr_4fs_merge_galah_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/lunarc/merge_spectra
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace
rsync -a ../workspace/turbospec_galah_v2_* ${TMPDIR}/workspace/
echo Rsync done: `date`
echo Running 4fs script: `date`

python2.7 merge_libraries.py --input-library turbospec_galah_v2

echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/turbospec_galah_v2 ../workspace
echo Rsync done: `date`

