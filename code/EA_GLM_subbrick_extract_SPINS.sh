#!/usr/bin/env bash

#SBATCH --job-name="EA_GLM_SPINS_subbrick_%A"
#SBATCH --cpus-per-task=2
#SBATCH --export=ALL
#SBATCH --output=/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/EA_GLM_subbrick_SPINS.txt
#SBATCH --error=/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/EA_GLM_subbrick_SPINS.err

# note that an error log file will also print to the directory you run this script from - you can change the output dir in the .py script

module load connectome-workbench/1.4.1

sublist=$(ls -d -- /projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/sub*/*mm*/)
#sublist=$(ls -d -- /projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/sub-CMH0002/*mm*/)

for dir in ${sublist}; do
    subid=$(echo $dir| cut -c 47-57)
    if [ ! -f ${dir}/*circle-block-tstat.dscalar.nii ]; then
    python3 /projects/loliver/SPINS_ASD_EA_GLM/code/EA_GLM_subbrick_extract.py ${dir} ${subid}
    fi
done


