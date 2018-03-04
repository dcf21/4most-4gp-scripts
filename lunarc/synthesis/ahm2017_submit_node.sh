#!/bin/sh
# document this script to stdout (assumes redirection from caller)
cat $0

# receive my worker number
export item=$1
export WRK_NB=$1

source activate myenv

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
cd ${HOME}/iwg7_pipeline/4most-4gp-scripts/synthesize_grids
python synthesize_ahm2017.py --every 80 --skip ${item} --create \
                                       --output-library turbospec_ahm2017_8element_sample_${item} \
                                       --elements Fe,Ca,Mg,Ti,Si,Na,Ni,Cr \
                                       --log-dir ../output_data/logs/turbospec_ahm2017_8element_sample_${item}

# rescue the results back to job directory
# cp -p result.dat ${JOB_DIR}

# clean up the local disk and remove the worker-private directory

# cd $SNIC_TMP
# rm -rf WRK_${WRK_NB}
