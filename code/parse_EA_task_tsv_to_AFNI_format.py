#!/usr/bin/env python
import argparse
import logging
import os
from glob import glob

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(
    "parse_EA_task_AFNI.log"
)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


# define savelist function for the 1D regressor files for EA button presses, circles button presses, and circles (just onset times, fixed duration)
# essentially takes the values/elements in n_array (onset times; defined later) and attaches them together in the format we need 

def savelist(n_array, val, sub_outpath):

    """
    inputs:

    n_array    array of integer/float

    val        a string describe output text file name

    outpath    path to output directory

    outputs:   a 1D text fille


    """
    sub_path = os.path.join(sub_outpath, val)
    myfile = open(sub_path, "a")
    logger.debug(myfile)
    for element in n_array:
        myfile.write(str(element) + " ")
    myfile.write("\n")
    myfile.close()


# define save_EA function for the EA pmod regressor files (different setup as we need onset, duration, and EA score for each video)     
# similarly takes the values/elements in EA_arr (onset, duration, EA score; defined later) and attaches them together in the format we need

def save_EA(EA_arr, subj, sub_outpath):
    """

    inputs:

    EA_arr    array of EA block onset

    subj      subject ID; 111

    outpath   a string represent path to output directory

    outputs:  EA pmod score, duration, and onset in AFNI 1D format

    """

    suffix = subj + "_EA.1D"
    sub_path = os.path.join(sub_outpath, suffix)
    myfile = open(sub_path, "a")
    logger.debug(myfile)
    for idx, val in enumerate(EA_arr):
        myfile.write(
            str(EA_arr[idx][0])
            + "*"
            + str(EA_arr[idx][2])
            + ":"
            + str(EA_arr[idx][1])
            + " "
        )
    myfile.write("\n")
    myfile.close()


# define convert_1D_format function to grab elements from EA tsvs needed for each regressor 

def convert_1D_format(sub_inpath, subid, sub_outpath):
    """

    inputs:

    input_dir    a fullpath to subject directory that contain the EA task tsv
                (i.e /archive/data/SPINS/data/nii/SPN01_CMH_0012_01)

    out_dir      a fullpath to subject output directory
                (i.e /projects/ttan/SPINS/AFNI/data/sub-CMH0012)

    """

    subj = "sub-" + subid
    tsv_files = sorted(glob(sub_inpath + "/" + "*EAtask_*.tsv"))

    if len(tsv_files) != 3:
        logger.critical(
            "Subject missing a EA task run at {}".format(sub_inpath)
        )
        sys.exit(1)

    # loop through tsv files and keep columns of interest in event_df
    # tsv_f = sorted([os.path.join(input_dir,f) for f in os.listdir(input_dir) if ("EAtask" in f)])
    for f in tsv_files:
        event_df = pd.read_csv(f, delimiter="\t")
        cols = [
            col
            for col in event_df.columns
            if col.startswith(
                (
                    "trial_type",
                    "onset",
                    "duration",
                    "block_score",
                    "stim_file",
                    "event",
                )
            )
        ]
        event_df = event_df[cols]
        event_df.loc[:, "onset"] = event_df["onset"].apply(lambda x: x - 8) # drops the first 4 TRs (8 s)
        
        # filter by column to get info of interest for each condition
        for col in event_df.columns:

            if col == "event_type":
                button_press = event_df[
                    event_df["event_type"] == "button_press"
                ]

                # Filter button press during EA stimulus
                EA_button_press = button_press[
                    button_press["stim_file"].str.match("NW|AR|TA|CT|ME|HR|DH")
                ]
                EA_butt_onset = EA_button_press["onset"].T.to_numpy()
                EA_butt_onset = np.around(EA_butt_onset, 4)
                val = subj + "_EA_buttons.1D"

                savelist(EA_butt_onset, val, sub_outpath)

                # Filter button press during circle stimulus
                circle_button_press = button_press[
                    button_press["stim_file"].str.match("circles")
                ]
                circle_butt_onset = circle_button_press["onset"].T.to_numpy()
                circle_butt_onset = np.around(circle_butt_onset, 4)
                val = subj + "_circle_buttons.1D"
                savelist(circle_butt_onset, val, sub_outpath)

            # circle blocks/videos
            if col == "trial_type":
                circle_block_onset = event_df[
                    event_df["trial_type"] == "circle_block"
                ]
                circle_arr = circle_block_onset["onset"].to_numpy()
                circle_arr = np.around(circle_arr, 4)
                val = subj + "_circles.1D"
                savelist(circle_arr, val, sub_outpath)

                # EA blocks/videos
                EA_videos = event_df[event_df["trial_type"] == "EA_block"]
                EA_arr = EA_videos[
                    ["onset", "duration", "block_score"]
                ].to_numpy()
                EA_arr = np.around(EA_arr, 4)
                save_EA(EA_arr, subj, sub_outpath)

    return (EA_butt_onset, circle_butt_onset, circle_arr, EA_arr)


# define function to call the whole script from the command line
def main():

    parser = argparse.ArgumentParser(
        description="Convert task tsv file to AFNI 1D"
    )
    parser.add_argument(
        "input_dir",
        type=str,
        help="path to directory that store task tsv files",
    )
    parser.add_argument(
        "sub_id", type=str, help='string of subject ID (i.e "CMH0012")'
    )
    parser.add_argument("out_dir", type=str, help="output path")

    args = parser.parse_args()
    inpath = args.input_dir
    subid = args.sub_id
    outdir = args.out_dir
    try:
        convert_1D_format(inpath, subid, outdir)
    except ValueError:
        logger.error(
            "format_confounds_tsv did not run because of missing input and output. Try again..."
        )


if __name__ == "__main__":
    main()
