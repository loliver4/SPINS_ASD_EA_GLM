#!/usr/bin/env python
import argparse
import logging
import os
import sys
from glob import glob

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(
    "parse_confounds_32p_no_GSR.log"
)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def format_confounds_tsv(sub_inpath, subid, sub_outpath):
    """
    input      full-path to the subject directory where the confounds tsv files are stored
               (i.e '/archive/data/SPINS/pipelines/bids_apps/fmriprep/sub-CMH0057/ses-01/func')

    output     a 1-D confound file including all runs
               (i.e '/projects/ttan/SPINS/AFNI/data/sub-CMH0012)

    """

    tsv_files = sorted(
        glob(sub_inpath + "/" + "*task-emp*confounds_fixedregressors.tsv")
    )
    print(tsv_files)
    # Check if there are 3 tsv files
    if len(tsv_files) != 3:
        logger.critical(
            "Subject missing an EA task run at {}".format(sub_inpath)
        )
        sys.exit(1)

    subj = "sub-" + subid
    combined_confounds_df = []
    for f in tsv_files:
        fixed_confound_df = pd.read_csv(f, delimiter="\t")
        confound_vars = [
            col
            for col in fixed_confound_df.columns
            if col.startswith(
                (
                    "white_matter",
                    "csf",
                    #"global_signal",
                    "trans",
                    "rot",
                )
            )
        ]
        fixed_confound_df = fixed_confound_df[confound_vars]
        fixed_confound_df = fixed_confound_df.drop("csf_wm", axis=1) # added as there is now a csf_wm confound var
        tr_drop = 4
        fixed_confound_df = fixed_confound_df.loc[tr_drop:].reset_index(
            drop=True
        )
        combined_confounds_df.append(fixed_confound_df)
    tmp_df = pd.concat(
        [
            combined_confounds_df[0],
            combined_confounds_df[1],
            combined_confounds_df[2],
        ],
        ignore_index=True,
        sort=False,
    )
    output = os.path.join(sub_outpath, subj + "_ea_confounds_no_GSR_glm.1D")
    print(output)
    tmp_df.to_csv(output, sep=" ", index=False, header=False)
    return tmp_df


def main():

    parser = argparse.ArgumentParser(description="Extract confound regressors")
    parser.add_argument(
        "input_dir",
        type=str,
        help="path to directory that store confound tsv files",
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
        format_confounds_tsv(inpath, subid, outdir)
    except ValueError:
        logger.error(
            "format_confounds_tsv did not run because of missing input and output. Try again..."
        )


if __name__ == "__main__":
    main()
