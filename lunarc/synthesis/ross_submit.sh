#!/bin/sh
# requesting the number of nodes needed
#SBATCH -N 4
#SBATCH --exclusive
#
# job time, change for what your job farm requires
#SBATCH -t 96:00:00
#
# job name and output file names
#SBATCH -J ross_farm
#SBATCH -o stdout_ross_farm_%j.out
#SBATCH -e stderr_ross_farm_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

source activate myenv

# set the number of jobs - change for your requirements
export NB_of_jobs=80

# Loop over the job number
for ((i=0; i<$NB_of_jobs; i++))
do
    srun -Q --exclusive -n 1 -N 1 \
        ross_submit_node.sh $i &> worker_${SLURM_JOB_ID}_${i} &
    sleep 1
done

# keep the wait statement, it is important!
wait

