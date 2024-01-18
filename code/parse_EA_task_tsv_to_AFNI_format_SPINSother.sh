#!/usr/bin/env bash
#SBATCH --partition=low-moby
#SBATCH --array=1-346
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#BSATCH --mem-per-cpu=1G
#SBATCH --time=1:00:00
#SBATCH --export=ALL
#SBATCH --job-name="parse_EA_task_tsv_to_AFNI_format"
#SBATCH --output=/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/logs/parse_EA_task_tsv_to_AFNI_format_SPINSother_%j.txt

# note that an error log file will also print to the directory you run this script from - you can change the output dir in the .py script

# this sublist includes site and ID number, without a dash
sublist="/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS/EA_task_1D_sublist_SPINSother.txt"
index () {
	  head -n $SLURM_ARRAY_TASK_ID $sublist \
	  | tail -n 1
	 }

sub_indir="/archive/data/SPINS/data/nii"
sub_outdir="/projects/loliver/SPINS_ASD_EA_GLM/data/SPINS"  
site=$(echo `index`| cut -c 1-3)
id=$(echo `index`| cut -c 4-7)
subj=`index`

python3 /projects/loliver/SPINS_ASD_EA_GLM/code/parse_EA_task_tsv_to_AFNI_format.py ${sub_indir}/SPN01_${site}_${id}_* ${subj} ${sub_outdir}/sub-${subj}

