#!/bin/sh
# document this script to stdout (assumes redirection from caller)
cat $0

# receive my worker number
export item=$1
export WRK_NB=$1

# activate conda python environment

# This line used to work up until Feb 2019...
source activate myenv

# ... but since it's stopped working, this line makes sure we use the right python ...
export PATH="/home/dominic/.conda/envs/myenv/bin:$PATH"

# create worker-private subdirectory in $SNIC_TMP
# export WRK_DIR=$SNIC_TMP/WRK_${WRK_NB}
# mkdir $WRK_DIR

# create a variable to address the "job directory"
# export JOB_DIR=$SLURM_SUBMIT_DIR/job_${WRK_NB}

# now copy the input data and program from there

# cd $JOB_DIR
# cp -p input.dat processor $WRK_DIR

# change to the execution directory
# cd $WRK_DIR

# run the program
cd ${HOME}/iwg7_pipeline/4most-4gp-scripts/src/scripts/synthesize_samples

echo Temporary directory: ${TMPDIR}/workspace
mkdir ${TMPDIR}/workspace

python synthesize_galah.py --every 80 --skip ${item} --create \
                           --workspace "${TMPDIR}/workspace" \
                           --output-library turbospec_galah_v2_${item} \
                           --log-dir ../../../output_data/logs/galah_stars_${item}

echo Starting rsync: `date`
rsync -a ${TMPDIR}/workspace/turbospec_* ../../../workspace
echo Rsync done: `date`

# rescue the results back to job directory
# cp -p result.dat ${JOB_DIR}

# clean up the local disk and remove the worker-private directory

# cd $SNIC_TMP
# rm -rf WRK_${WRK_NB}
