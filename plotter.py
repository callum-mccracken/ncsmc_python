"""functions for making plots related to ncsmc output"""

from os.path import join, exists
from os import mkdir
from math import inf

import matplotlib.pyplot as plt

from utils import output_dir, make_nice_title
from flipper import separate_into_channels, flip

# file details
filename = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/to_be_flipped/big_eigenphase_shift.agr_flipped"
flipped = True

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

energy_bounds = (0,5)  # if you don't want bounds use (-inf, inf)



def plot_single_channel(energies, phases, title):
    """Plot (with matplotlib) the data from a single channel"""
    # energies may be longer than phases,
    # so we add zeros to the start if needed
    len_diff = len(energies) - len(phases)
    phases = [0 for _ in range(len_diff)] + phases
    # by the way we're guaranteed that phases starts at 0 so we won't have jumps
    plt.title(title)
    plt.ylabel("Phase (degrees)")
    plt.xlabel("Energy (MeV)")
    plt.plot(energies, phases)
    if not exists(join(output_dir, "PNGs")):
        mkdir(join(output_dir, "PNGs"))
    plt.savefig(join(output_dir, "PNGs", title+".png"))
    plt.clf()
    plt.close()

def multi_channel_plot(filename, already_flipped, energy_bounds, output_type="matplotlib", channels=channels_to_plot):
    """makes one plot with all user-specified channels"""
    lines = channels.split("\n")
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
        plt.xlabel("Energy (MeV)")
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
                for e, p in zip(energies, phases):
                    if l_bound <= e and e <= r_bound:
                        plot_energies.append(e)
                        plot_phases.append(p)
                # save channel to a file too, so we can use it later
                if not exists(join(output_dir, "CSVs")):
                    mkdir(join(output_dir, "CSVs"))
                csv_name = join(output_dir, "CSVs", nice_title+".csv")
                with open(csv_name, "w+") as csv_file:
                    for e, p in zip(plot_energies, plot_phases):
                        csv_file.write(",".join([str(e), str(p)]) + "\n")
                plt.plot(plot_energies, plot_phases, label=nice_title)

        plt.legend(loc='upper right', shadow=False, fontsize='xx-small')
        plt.savefig(join(output_dir, "multi_channel_plot.png"))
        plt.clf()
        plt.close()
    else:
        raise ValueError("output type "+str(output_type)+" not supported yet!")
    
    print("done plotting")

multi_channel_plot(filename, flipped, energy_bounds, channels=channels_to_plot)
