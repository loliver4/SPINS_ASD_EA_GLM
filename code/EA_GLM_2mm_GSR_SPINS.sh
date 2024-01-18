#!/usr/bin/env bash
#SBATCH --partition=low-moby
#SBATCH --array=1-438
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#BSATCH --mem-per-cpu=1G
#SBATCH --time=12:00:00
#SBATCH --export=ALL
#SBATCH --job-name="EA_GLM_2mm_GSR_SPINS"
#SBATCH --output=/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/logs/EA_GLM_2mm_GSR_SPINS_%j.txt

# you may need to update the log file and tmp output directories in the .py script

module load connectome-workbench/1.4.1
module load AFNI/2017.07.17

sublist="/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/3dDeconvolve_sublist.txt"
index () {
	  head -n $SLURM_ARRAY_TASK_ID $sublist \
	  | tail -n 1
	 }

sub_in=/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/sub-`index`/
sub_out=/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/sub-`index`/2_mm

if [ ! -f ${sub_out}/*glm_ea_1stlevel.dscalar.nii ]; then
   python3 /projects/loliver/SPINS_ASD_EA_GLM/code/EA_GLM_2mm_GSR.py ${sub_in} ${sub_out} `index`
fi
