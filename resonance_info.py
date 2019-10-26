"""contains function which finds resonances in ncsmc data"""
from os.path import join
import argparse

import flipper
import utils

filename = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/to_be_flipped/big_eigenphase_shift.agr_flipped"
flipped = True

def get_resonance_info(filename, already_flipped=False):
    """Takes a ncsmc filename and writes info about each channel to a CSV
    file, with information about whether or not there is a resonance there."""
    filename = utils.abs_path(filename)
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
    res_file_name = join(utils.output_dir, "resonance_info.csv")
    with open(res_file_name, "w+") as res_file:
        res_file.write("2J,parity,2T,column_number,resonance_type\n")
        for title, res_type in resonance_info.items():            
            Jx2, parity, Tx2, _, column_number = title.split("_")
            write_list = [Jx2, parity, Tx2, column_number, res_type]
            res_file.write(",".join(write_list) + "\n")
    print("Analyzed all channels, saved CSV with info to", res_file_name)
    return res_file_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Resonance Finder")
    parser.add_argument(
        "-f", nargs='?', const=None, help="full path to file", type=str)
    args = parser.parse_args()
    if args.f is not None:
        get_resonance_info(args.f)
    else:
        get_resonance_info(filename, already_flipped=flipped)