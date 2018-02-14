#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 24:00:00
#
# job name and output file names
#SBATCH -J splitter
#SBATCH -o stdout_split_%j.out
#SBATCH -e stderr_split_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/degrade_spectra/
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/cannon_59052_0
mkdir ${TMPDIR}/cannon_59052_0
rsync -a ../workspace/galah_test_sample_turbospec ${TMPDIR}/cannon_59052_0/
echo Rsync done: `date`
echo Running rearrange script: `date`

python2.7 redden_library.py --input-library galah_test_sample_turbospec \
                            --workspace "${TMPDIR}/cannon_59052_0" \
                            --output-library galah_test_sample_reddened \

echo Starting rsync: `date`
rsync -a ${TMPDIR}/cannon_59052_0/galah_test_sample_reddened ../workspace
echo Rsync done: `date`

