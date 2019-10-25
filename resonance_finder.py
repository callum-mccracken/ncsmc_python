"""contains function which finds resonances in ncsmc data"""

from flipper import flip, separate_into_channels
from plotter import plot_single_channel
from utils import make_nice_title, output_dir

import matplotlib.pyplot as plt
from os.path import join, exists
from os import mkdir

filename = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/to_be_flipped/big_eigenphase_shift.agr_flipped"
flipped = True

def find_resonances(filename, already_flipped=False):
    """Takes a ncsmc filename and detects / plots all resonances"""
    # first flip the file if needed
    if already_flipped:
        new_filename = filename
    else:
        new_filename = flip(filename)

    print("finding resonances")
    
    # channels: dict, key = title, value = list with channel numbers
    # energies is a list of energy values, possibly longer than some channels
    channels, energies = separate_into_channels(new_filename)

    # now look in each channel for a resonance
    resonance_info = {}
    for title, phases in channels.items():
        nice_title = make_nice_title(title)

        resonance = False
        maybe_resonance = False

        # TODO: is there a better way of looking for resonances?

        max_difference = abs(max(phases) - min(phases))
        
        if max_difference > 60:
            maybe_resonance = True
            res_type = "possible"
        if max_difference > 90:
            resonance = True
            res_type = "strong"

        if maybe_resonance:  # this applies for strong resonances too
            resonance_info[nice_title] = res_type
        if resonance:  # only plot strong resonances though
            plot_single_channel(energies, phases, nice_title)
    # write resonance info to a file
    res_file_name = join(output_dir, "resonance_info.csv")
    with open(res_file_name, "w+") as res_file:
        res_file.write("2J,parity,2T,column_number,resonance_type\n")
        for title, res_type in resonance_info.items():            
            Jx2, parity, Tx2, _, column_number = title.split("_")
            write_list = [Jx2, parity, Tx2, column_number, res_type]
            res_file.write(",".join(write_list) + "\n")
    print("found resonances, made plots, made resonance_info.txt file")
    return res_file_name

if __name__ == "__main__":
    find_resonances(filename, already_flipped=flipped)