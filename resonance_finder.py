from flipper import flip, separate_into_channels
import matplotlib.pyplot as plt
from os.path import realpath, split, join, exists
import os
import argparse
from math import inf
filename = "/Users/callum/Desktop/rough_python/ncsmc_resonance_finder/to_be_flipped/big_eigenphase_shift.agr_flipped"

# copy lines from resonance_info.csv here, when running multi_channel_plot()
# format: 2J, parity, 2T, column_number, resonance_type
# blank lines are okay, but no extra spacing please!
channels_to_plot = """
2,-,0,2,strong
2,-,2,1,strong
2,-,2,2,strong
2,+,2,1,strong
2,+,2,4,strong
4,-,0,1,strong
4,-,2,1,strong
4,-,2,2,strong
4,+,0,1,strong
4,+,2,2,strong
6,-,0,2,strong
6,-,2,1,strong
6,-,2,2,strong
6,+,2,2,strong
8,-,0,1,strong
8,-,2,1,strong
8,-,2,2,strong
10,-,0,1,strong
10,-,2,2,strong
"""

# make directory where we'll store images of resonances etc
output_dir = join(os.getcwd(), "resonances")
if not exists(output_dir):
    os.mkdir(output_dir)

def multi_strip(string, list_of_strs):
    """
        Returns the string but stripped of substrings
        Same idea as string.strip(), but for many arguments
    """
    for s in list_of_strs:
        if s == "":  # ignore this case
            continue
        while s in string:
            string = string.replace(s, "")
    return string

def make_nice_title(title):
    # we'll want a good title for plotting etc.
    nice_title = multi_strip(title, ["\n", "\\", "S", "N", "@", "legend"])
    # remove s0, s1, ..., (the first word), that's just used for xmgrace
    nice_title = nice_title[nice_title.index('"'):]
    # remove quotes and replace spaces with underscores
    nice_title = nice_title.replace('"', "").replace(" ", "_")
    # put underscores between 2J, parity, 2T
    if "+" in nice_title:
        parity_index = nice_title.index("+")
        parity = "+"
    elif "-" in nice_title:
        parity_index = nice_title.index("-")
        parity = "-"
    else:
        raise ValueError("your resonance doesn't have a parity specified, title is "+title)
    nice_title = (nice_title[:parity_index]
        + "_" + parity + "_" + nice_title[parity_index+1:])
    return nice_title

def plot_single_channel(energies, phases, title):
    # energies may be longer than phases,
    # so we add zeros to the start if needed
    len_diff = len(energies) - len(phases)
    phases = [0 for _ in range(len_diff)] + phases
    # by the way we're guaranteed that phases starts at 0
    plt.title(title)
    plt.ylabel("Phase (degrees)")
    plt.xlabel("Energy")
    plt.plot(energies, phases)
    plt.savefig(join(output_dir, title+".png"))
    plt.clf()

def find_resonances(filename):
    """Takes a ncsmc filename and detects / plots all resonances"""
    # first flip the file
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

        max_difference = abs(max(phases) - min(phases))
        
        if max_difference > 60:
            maybe_resonance = True
            res_type = "possible"
        if max_difference > 90:
            resonance = True
            res_type = "strong"

        if maybe_resonance:  # this applies for strong resonances too
            resonance_info[nice_title] = res_type
        if resonance:  # only plot strong resonances
            plot_single_channel(energies, phases, nice_title)
    
    # write resonance info
    with open(join(output_dir, "resonance_info.csv"), "w+") as res_file:
        res_file.write("2J,parity,2T,column_number,resonance_type\n")
        for title, res_type in resonance_info.items():            
            Jx2, parity, Tx2, _, column_number = title.split("_")
            write_list = [Jx2, parity, Tx2, column_number, res_type]
            res_file.write(",".join(write_list) + "\n")

    print("found resonances, made plots, made resonance_info.txt file")

def multi_channel_plot(filename, already_flipped=False, energy_bounds=(-inf, inf), output_type="matplotlib"):
    """makes one plot with all user-specified channels"""
    # note: we get channels_to_plot from further up in the file
    lines = channels_to_plot.split("\n")
    input_titles = []
    for line in lines:
        if line == "":
            continue
        Jx2, parity, Tx2, col_num, _ = line.split(",")
        title = "_".join([Jx2, parity, Tx2, "column", col_num])
        input_titles.append(title)

    # ensure file is properly formatted
    if already_flipped:
        print("assuming file does not need to be flipped")
        new_filename = filename
    else:
        print("before making multi_channel_plot, ensuring file is correct")
        new_filename = flip(filename)
    

    print("now working on plotting")
    
    # channels: dict, key = title, value = list with channel numbers
    # energies is a list of energy values, possibly longer than some channels
    channels, energies = separate_into_channels(new_filename)

    l_bound, r_bound = energy_bounds

    if output_type == "matplotlib":
        # set up plot
        plt.title("Multi-Channel Plot")
        plt.ylabel("Phase (degrees)")
        plt.xlabel("Energy")
        # now look in each channel, plot the ones we care about
        for title, phases in channels.items():
            # see if the title matches one we were given. If so, plot
            nice_title = make_nice_title(title)
            if nice_title in input_titles:
                print("adding", nice_title, "to plot")
                # energies may be longer than phases,
                # so we add zeros to the start if needed
                len_diff = len(energies) - len(phases)
                phases = [0 for _ in range(len_diff)] + phases
                plot_energies = []
                plot_phases = []
                for i, e in enumerate(energies):
                    if l_bound <= e and e <= r_bound:
                        plot_energies.append(e)
                        plot_phases.append(phases[i])
                plt.plot(plot_energies, plot_phases, label=nice_title)

        plt.legend(loc='upper right', shadow=False, fontsize='xx-small')
        plt.savefig(join(output_dir, "multi_channel_plot.png"))
        plt.clf()
    else:
        raise ValueError("output type "+str(output_type)+" not supported yet!")
    print("plot saved")
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Resonance Finder")
    parser.add_argument(
        "-f", nargs='?', const=None, help="full path to file", type=str)
    args = parser.parse_args()
    if args.f is not None:
        find_resonances(args.f)
    else:
        find_resonances(filename)
        multi_channel_plot(filename, already_flipped=True, energy_bounds=(0,5))