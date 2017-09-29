#!/bin/sh
# requesting the number of nodes needed
#SBATCH -N 4
#SBATCH --exclusive
#
# job time, change for what your job farm requires
#SBATCH -t 04:00:00
#
# job name and output file names
#SBATCH -J ahm2017_farm
#SBATCH -o stdout_ahm2017_farm_%j.out
#SBATCH -e stderr_ahm2017_farm_%j.out
cat $0

module add GCC/5.4.0-2.26  OpenMPI/1.10.3  scipy/0.17.0-Python-2.7.11  SQLite/3.20.1  SQLite/3.9.2

# set the number of jobs - change for your requirements
export NB_of_jobs=80

# Loop over the job number
for ((i=0; i<$NB_of_jobs; i++))
do
    srun -Q --exclusive -n 1 -N 1 \
        ahm2017_submit_node.sh $i &> worker_${SLURM_JOB_ID}_${i} &
    sleep 1
done

# keep the wait statement, it is important!
wait

