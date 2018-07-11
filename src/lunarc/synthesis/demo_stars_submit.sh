#!/bin/sh
# requesting the number of nodes needed
#SBATCH -N 1
#SBATCH --exclusive
#SBATCH --qos=test
#
# job time, change for what your job farm requires
#SBATCH -t 00:30:00
#
# job name and output file names
#SBATCH -J demo_stars_farm
#SBATCH -o stdout_demo_stars_farm_%j.out
#SBATCH -e stderr_demo_stars_farm_%j.out
cat $0

module add GCC/4.9.3-binutils-2.25  OpenMPI/1.8.8 CFITSIO/3.38  GCCcore/6.4.0 SQLite/3.20.1 Anaconda2

# activate python environment
source activate myenv

# set the number of jobs - change for your requirements
export NB_of_jobs=20

# Loop over the job number
for ((i=0; i<$NB_of_jobs; i++))
do
    srun -Q --exclusive -n 1 -N 1 \
        demo_stars_submit_node.sh $i &> worker_${SLURM_JOB_ID}_${i} &
    sleep 1
done

# keep the wait statement, it is important!
wait

