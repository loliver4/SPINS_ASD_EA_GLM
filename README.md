# Empathic Accuracy GLM  

This directory contains scripts to wrangle data and generate files needed to run the EA GLM with 2 mm and 6mm smoothing, and with and without GSR for SPINS and SPASD participants.  

**Data** directory is where outputs are stored before being moved to the archive (/archive/data/SP*/pipelines/ea_glm).  

**Code** directory includes scripts to run the EA GLM and generate files needed for analyses:  
Activate corresponding python env before running any .py scripts using source /projects/loliver/SPINS_ASD_EA_GLM/code/py_venv/bin/activate (see note below re this)  
1) cifti_clean_EA_*mm_*.sh to smooth outputs (2 or 6 mm) and drop first 4 TRs after fmriprep and ciftify have been run  
2) parse_EA_task_tsv_to_AFNI_format_*.sh (which runs parse_EA_task_tsv_to_AFNI_format.py) to generate 1D regressor files needed for the GLM from the EA task tsvs  
     For ZHP participants specifically (see below): parse_EA_task_tsv_to_AFNI_format_ZHP.sh (which runs parse_EA_task_tsv_to_AFNI_format_ZHP.py); SPINSother refers to SPINS participants other than ZHP  
3) parse_confounds_*.sh (which runs corresponding parse_confounds_*.py, with GSR (36p) or without GSR (32p)) to generate confound regressor file needed for the GLM  
4) EA_GLM_*mm_*.sh (which runs corresponding EA_GLM_*mm_*.py, with 2 or 6 mm smoothing, and with or without GSR) to run the EA GLM  
5) EA_GLM_subbrick_extract_*.sh (which runs EA_GLM_subbrick_extract.py) to extract coefficients and t-stat maps for further analyses (e.g., PALM)  
6) rename_GLM_files.sh to rename the residual and design matrix files in line with the extracted subbricks (optional)  

If you want to extract time series data from the residual GLM outputs using the Glasser and Tian atlases, scripts to do that can be found here: /projects/loliver/SPINS_PLS_Conn/code/extract_time_series_*.sh  


## Important GLM Notes:
For the SPINS ZHP scans only (Zucker Hillside Prisma), the trigger occurred prior to dummy scan collection (6000 ms duration), after which data acquistiion actually began. Thus, onset times need to be adjusted by subtracting 6000 ms from the recorded video onset time - trigger time. This was fixed September 14, 2022.  

GLM code and data in this directory include the -stim_times_subtract = -1 option for 3dDeconvolve, which subtracts the specified number of seconds from each time encountered in any '-stim_times*' option (or in this case adds 1 second).  The purpose of this option is to make it simple to adjust timing files for the removal of images from the start of each imaging run.  

This was implemented based on the recommendation from this post https://reproducibility.stanford.edu/slice-timing-correction-in-fmriprep-and-linear-modeling, which essentially outlines that fMRIprep registers to the middle slice of a TR for slice timing correction by default but linear modeling using AFNI's 3dDeconvolve (and nilearn) assumes that the data are acquired at time zero.  

Note: The -stim_times_subtract option is included in the model.py script for 3dDeconvolve in nipype   

From the post:
Slice timing correction is enabled by default in fMRIprep and is performed using the AFNI 3dTshift function. This function takes an argument called -tzero that specifies which slice time to register to, which defaults to "the average of the 'tpattern' values (either from the dataset header or from the -tpattern option)" - that is, the middle slice in time.   

If you use FSL or SPM to analyze the data, both software packages default to creating regressors such that the assumption is that all slices were acquired simultaneously halfway through the TR. This is done regardless of using STC (since there is generally no way for the sotware to know whether STC was applied or not). Thus, the regressors and fMRIPrepped data using STC should match up correctly; if STC is not applied, there will be a mismatch between the data and model (as shown above), which will be zero on average across slices but ranges from -TR/2 for the first slice to TR/2 for the last slice.  

If you’re using nilearn (which is used within fitlins to estimate the model) and you would like to ensure that the model and data are aligned, you can simply shift the values in the frame_times by +TR/2.  

If you use AFNI's 3dDeconvolve/3dREMLfit to model your data, then you can set the -stim_times_subtract option equal to -TR/2 (since we actually want to lengthen the stimulus times by TR/2) when creating the matrix using 3dDeconvolve.  

Another general strategy in cases where the model assumes that the data are acquired at time zero (as in nilearn and AFNI) is to add TR/2 to the event onsets.   


## Virtual environment notes:
The nipype 3dDeconvolve interface doesn’t include some 3dDeconvolve options by default (AM2 option, polort A, xjpeg, residuals and full model), so the corresopnding model.py script in the virtual env needed to be updated accordingly (the AM2 option in particular is needed for parametric modulation)  
Here, /projects/loliver/SPINS_ASD_EA_GLM/code/py_venv/lib/python3.8/site-packages/nipype/interfaces/afni/model.py  
It's probabyly easiest to copy or use this virtual env vs making these changes yourself if you are re-running this.  

polort A addition:  
polort_A = traits.Str(
        desc="Set the polynomial order automatically " "[default: A]",
        argstr="-polort %s",
    )  

AM2 addition:  
num_stimts = traits.Int(
        desc="number of stimulus timing files",
        argstr="-num_stimts %d",
        position=-6,
    )
 stim_times_AM2 = traits.List(
        traits.Tuple(
        traits.Int(desc="k-th R model"),         File(
                 desc="stimulus timing file with different duration to class k"
             ),
             Str(desc="model"),
         ),
         desc="generate two resonpose models: one with th emean amplittude and one with the differences from the mean.",
         argstr="-stim_times_AM2 %d %s '%s'...",
         position=-6,
     )  

Then need to change num_stimts position to -7  

Also need to change:  
stim_label = traits.List(
        traits.Tuple(
            traits.Int(desc="k-th input stimulus"), Str(desc="stimulus label")
        ),
        desc="label for kth input stimulus (e.g., Label1)",
        argstr="-stim_label %d %s...",
        requires=["stim_times", "stim_times_AM2"], ## THIS LINE RIGHT HERE
        position=-4,
    )  

xjpeg:  
xjpeg = File(
        desc="specificy name for a JPEG file graphing the X matrix",
        argstr="-xjpeg %s",
    )  

residuals and full model:  
res_file = File(desc="output residual files", argstr="-errts %s")
    full_model = File(
        desc="output the (full model) time series fit to the input data",
        argstr="-fitts %s",
    )  

Also need to comment out REML outputs (different model type):  
class DeconvolveOutputSpec(TraitedSpec):
    out_file = File(desc="output statistics file", exists=True)
    \#reml_script = File(
    \#    desc="automatical generated script to run 3dREMLfit", exists=True
    \#)  

 \# outputs["reml_script"] = self._gen_fname(suffix=".REML_cmd", **_gen_fname_opts)  


## Other Notes:  
Original sublists were copied from Thomas' SPINS and SPASD dirs (e.g., /projects/ttan/SPINS/lists) and modified from there.  

SPASD sub-CMP0074 is missing EA log files, sub-CMP0076 only completed EA Run 1, and sub-CMP0085 only completed EA Runs 1 and 2. SPASD sub-CMP0014 had two nan values in their EA 1D regressor file - changed to 0 and reran (excluded based on EA task performance anyway).  

SPINS participants with nan values in their EA 1D regressor files:  
sub-CMH0036
sub-CMH0046
sub-CMH0052
sub-CMH0059
sub-CMH0070
sub-CMH0097
sub-CMH0104
sub-CMH0155
sub-CMP0207
sub-MRC0001
sub-MRC0008
sub-MRC0012
sub-MRC0047
sub-MRP0099
sub-MRP0121
sub-ZHH0022
sub-ZHH0044
sub-ZHH0045
sub-ZHH0052
sub-ZHH0054
sub-ZHH0057
sub-ZHP0065
sub-ZHP0095
sub-ZHP0098
sub-ZHP0103
sub-ZHP0105
sub-ZHP0119
sub-ZHP0129
sub-ZHP0144
sub-ZHP0168  

nan values in EA 1D regressor files occur when a participant's EA responses can't be correlated with the target's responses due to a lack of responding during the task. The GLM will not run successfully in this case.   

Thomas updated nan values to 0 for SPINS participants to allow the GLM to run successfully and I did the same for SPINS ZHP participants who had nan values when they were rerun. All of these SPINS participants do not pass EA task QC (any videos with no responses, or more than 1 video with 1 button press, and any circle block score <0.2) anyway. Confirmed this is still the case after we updated EA Task QC inclusion/exclusion criteria in Oct, 2021.  

