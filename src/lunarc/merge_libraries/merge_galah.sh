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

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda3

# This line used to work up until Feb 2019...
source activate myenv

# ... but since it's stopped working, this line makes sure we use the right python ...
export PATH="/home/dominic/.conda/envs/myenv/bin:$PATH"

# rsync all the libraries we're going to merge onto temporary local storage
# this is hideously wasteful, but lunarc breaks otherwise
cd /projects/astro3/nobackup/dominic/iwg7_pipeline/4most-4gp-scripts/src/lunarc/merge_libraries
echo Starting rsync: `date`
echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace
rsync -a ../../workspace/turbospec_galah_v2_* ${TMPDIR}/workspace/
echo Rsync done: `date`
echo Running 4fs script: `date`

# do the merger
python3 merge_libraries.py --workspace "${TMPDIR}/workspace" --input-library turbospec_galah_v2

# rsync the result back to where we want it
echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/turbospec_galah_v2 ../../workspace
echo Rsync done: `date`
