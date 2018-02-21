#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 48:00:00
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
rsync -a ../workspace/demo_stars ${TMPDIR}/cannon_59052_0/
echo Rsync done: `date`
echo Running rearrange script: `date`

python2.7 degrade_library_with_4fs.py --input-library demo_stars \
                                      --workspace "${TMPDIR}/cannon_59052_0" \
                                      --snr-list 50 \
                                      --output-library-lrs 4fs_demo_stars_test_lrs \
                                      --output-library-hrs 4fs_demo_stars_test_hrs

echo Starting rsync: `date`
rsync -a ${TMPDIR}/cannon_59052_0/4fs_demo_stars_test_* ../workspace
echo Rsync done: `date`

