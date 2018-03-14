#!/bin/sh
# requesting the number of nodes needed
#
# job time, change for what your job requires
#SBATCH -t 24:00:00
#
# job name and output file names
#SBATCH -J redden_ahm2017
#SBATCH -o stdout_redden_ahm2017_%j.out
#SBATCH -e stderr_redden_ahm2017_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/degrade_spectra/
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace
rsync -a ../workspace/turbospec_ahm2017_perturbed ${TMPDIR}/workspace/
echo Rsync done: `date`
echo Running reddening script: `date`

python2.7 redden_library.py --input-library turbospec_ahm2017_perturbed \
                            --workspace "${TMPDIR}/workspace" \
                            --output-library reddened_ahm2017_perturbed

echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/reddened_* ../workspace
echo Rsync done: `date`

