"""
Contains a function which looks through ncsmc data and figures out which
channels have a resonance, which ones have a potential resonance,
and which ones have no resonance. Writes data to a csv file.

Can be run with

``python resonance_info.py -f /path/to/some/file``

(assumes file is not flipped)
"""
import os
from os.path import join, exists
import argparse

import flipper
import utils

filename = "/path/to/eigenphase_shift.agr_flipped"
flipped = True  # has the file at the path above been run through flipper.py?


def get_resonance_info(filename, Nmax=None, already_flipped=False):
    """
    Parses a ncsmc (eigen)phase shift file and writes info about each
    channel to a .csv file, with information about whether or not there is a
    resonance there. Returns name of said .csv file

    filename: path to phase shift file

    Nmax: integer, max number of excitations allowed

    already_flipped: boolean, whether or not the file has already been
    "flipped" by flipper.py
     """
    filename = utils.abs_path(filename)
    phase_word = "Eigenphase" if "eigen" in filename else "Phase"

    if Nmax is None:
        Nmax = int(input("What is Nmax? Enter an integer: "))

    # first flip the file if needed
    if already_flipped:
        new_filename = filename
    else:
        new_filename = flipper.flip(filename)

    print("Finding resonances...\r", end="")

    # channels: dict, key = title, value = list with channel numbers
    channels, _ = flipper.separate_into_channels(new_filename)

    # now look in each channel for a resonance
    resonance_info = {}
    for title, phases in channels.items():
        nice_title = utils.make_nice_title(title)

        resonance = False
        max_difference = abs(max(phases) - min(phases))

        if max_difference > 90:
            resonance = True
            res_type = "strong"
        elif max_difference > 60:
            res_type = "possible"
        else:
            res_type = "none"

        resonance_info[nice_title] = res_type

        if resonance:
            # anything we should do here?
            pass

    # write resonance info to a file, (res = resonance)
    output_dir = utils.output_dir.format(Nmax)
    if not exists(output_dir):
        os.mkdir(output_dir)
    res_file_title = "resonances_"+phase_word.lower()+"_Nmax_"+str(Nmax)+".csv"
    res_file_name = join(output_dir, res_file_title)
    with open(res_file_name, "w+") as res_file:
        res_file.write("2J,parity,2T,column_number,resonance_type\n")
        for title, res_type in resonance_info.items():
            Jx2, parity, Tx2, _, column_number = title.split("_")
            write_list = [Jx2, parity, Tx2, column_number, res_type]
            res_file.write(",".join(write_list) + "\n")
    print("Analyzed all channels, saved CSV with info to", res_file_name)
    return res_file_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Resonance Info")
    parser.add_argument("-f", nargs='?', const=None, help="filepath", type=str)
    args = parser.parse_args()
    if args.f is not None:
        get_resonance_info(args.f)
    else:
        get_resonance_info(filename, already_flipped=flipped)
