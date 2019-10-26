"""functions for making plots related to ncsmc output"""
from os.path import join, exists
import os
from math import inf
import argparse

import matplotlib.pyplot as plt

import utils
import flipper
from resonance_info import find_resonances

# File path (relative paths are okay)
filepath = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/to_be_flipped/big_eigenphase_shift.agr"

# Has the file already been "flipped"?
flipped = False

# Which channels should be added to the multi channel plot?
# format: 2J, parity, 2T, column_number, resonance_type
# e.g.    2,+,4,1,strong
# blank lines are okay, but no extra spacing please!
# (just paste into the space between the pair of triple quotes)
channels_to_plot = """



"""

# Controls what bounds to use for energy axis,
# e.g. if you have 0-10 but only want 0-5, set this to (0, 5)
# If you don't want bounds set this to (-inf, inf)
energy_bounds = (-inf, inf)

# even if you only want one type, put it inside a list (square brackets)!
output_types = ["matplotlib", "xmgrace"]  # what kind of output(s) do you want?

# types of resonances to plot. Possible values: "strong", "possible", "none"
res_types = ["strong"]

def plot(filename, flipped=False, e_bounds=(-inf, inf),
         res_types=["strong", "possible"],
         output_types=["matplotlib", "xmgrace"], channels=""):
    """
    Makes a whole bunch of plots.
    - one for each of the user-specified channels
    - one with all channels on the same plot
    """
    filename = utils.abs_path(filename)
    # ensure file is flipped
    if flipped:
        new_filename = filename
    else:
        new_filename = flipper.flip(filename)

    # if channels are provided, there will be at least one number in the string
    # if no channels are provided, get them all
    if not any([utils.is_float(char) for char in channels_to_plot]):
        # get csv filename with resonance info
        res_output_file = find_resonances(filename, already_flipped=True)
        # take all channels, i.e. all text in the file
        with open(res_output_file, "r+") as channel_file:
            channels = channel_file.read()

    print("Making multi-channel plot...")

    # make channel titles
    lines = channels.split("\n")
    input_titles = []
    for line in lines:
        if line == "":
            continue
        Jx2, parity, Tx2, col_num, res_type = line.split(",")
        # only take the types of resonances we want to plot
        if res_type in res_types:  
            title = "_".join([Jx2, parity, Tx2, "column", col_num])
            input_titles.append(title)

    # channels: dict, key = title, value = list with channel numbers
    # energies is a list of energy values, possibly longer than some channels
    channels, energies = flipper.separate_into_channels(new_filename)

    l_bound, r_bound = e_bounds

    # The following if blocks contain a bunch of repeated logic,
    # but I think it's better to have them separate, since if we merge them,
    # we'd have to have if blocks every few lines to call plotting functions.
    # This also means we can add new output types more easily (hopefully).

    main_plot_paths = []

    png_dir = join(utils.output_dir, "PNGs")
    csv_dir = join(utils.output_dir, "CSVs")
    grace_dir = join(utils.output_dir, "grace_files")
    for d in [png_dir, csv_dir, grace_dir]:
        if not exists(d):
            os.mkdir(d)

    if "matplotlib" in output_types:
        print("Working on output type 'matplotlib'...")
        

        # now look in each channel, plot the ones we care about
        to_plot = []
        for title, phases in channels.items():
            # see if the title matches one we were given. If so, plot
            nice_title = utils.make_nice_title(title)
            if nice_title in input_titles:
                print("adding", nice_title, "to plot\r", end="")
                # energies may be longer than phases,
                # so we add zeros to the start of phases if needed
                len_diff = len(energies) - len(phases)
                phases = [0 for _ in range(len_diff)] + phases
                plot_energies = []
                plot_phases = []
                for e, p in zip(energies, phases):
                    if l_bound <= e and e <= r_bound:
                        plot_energies.append(e)
                        plot_phases.append(p)

                # make a channel plot
                c_fig, c_ax = plt.subplots()
                c_ax.set_title(nice_title)
                c_ax.set_ylabel("Phase (degrees)")
                c_ax.set_xlabel("Energy (MeV)")
                c_ax.plot(plot_energies, plot_phases)
                c_fig.savefig(join(png_dir, nice_title+".png"))
                plt.close(c_fig)
                
                # save channel to a file too, so we can use it later
                csv_name = join(csv_dir, nice_title+".csv")
                with open(csv_name, "w+") as csv_file:
                    for e, p in zip(plot_energies, plot_phases):
                        csv_file.write(",".join([str(e), str(p)]) + "\n")
                to_plot.append((plot_energies, plot_phases, nice_title))


        # set up main plot
        plt.title("Multi-Channel Plot")
        plt.ylabel("Phase (degrees)")
        plt.xlabel("Energy (MeV)")
        for energy, phase, title in to_plot:
            plt.plot(energy, phase, label=title)
        main_plot_path = join(png_dir, "multi_channel_plot.png")
        plt.legend(loc='upper right', shadow=False, fontsize='xx-small')
        plt.savefig(main_plot_path)
        main_plot_paths.append(main_plot_path)
    if "xmgrace" in output_types:
        print("Working on output type 'xmgrace'...")
        grace_string = ""  # string for the full file
        channel_string = ""  # string for each individual channel
        series_counter = 1  # for series titles
        # now look in each channel, plot the ones we care about
        for title, phases in channels.items():
            # see if the title matches one we were given. If so, plot
            nice_title = utils.make_nice_title(title)
            if nice_title in input_titles:
                print("adding", nice_title, "to plot\r", end="")
                # energies may be longer than phases,
                # so we add zeros to the start of phases if needed
                len_diff = len(energies) - len(phases)
                phases = [0 for _ in range(len_diff)] + phases
                plot_energies = []
                plot_phases = []
                for e, p in zip(energies, phases):
                    if l_bound <= e and e <= r_bound:
                        plot_energies.append(e)
                        plot_phases.append(p)

                # format output for channel file
                # start off with a title
                c_title = utils.xmgrace_title(title, series_counter) + "\n"
                channel_string = c_title
                series_counter += 1
                # add the values
                for e, p in zip(plot_energies, plot_phases):
                    channel_string += str(e) + " " + str(p) + "\n"
                # don't forget the &!
                channel_string += "&\n"
                # add this string to the main file
                grace_string += channel_string

                # before we save this channel, set series number to 1
                lines = channel_string.splitlines()
                lines[0] = utils.xmgrace_title(lines[0], 1)
                channel_string = "\n".join(lines)

                # save channel to the output file
                grdt_name = join(grace_dir, nice_title+".grdt")
                with open(grdt_name, "w+") as channel_file:
                    channel_file.write(channel_string)
        main_plot_path = join(grace_dir, "multi_channel_plot.grdt")
        # write overall file
        with open(main_plot_path, "w+") as grace_file:
            grace_file.write(grace_string)
        main_plot_paths.append(main_plot_path)
    # ensure that in your output_type's if block,
    # you set main_plot_path to something useful!
    print("Done plotting! Saved main plot(s) to:")
    for path in main_plot_paths:
        print(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Resonance Plotter")
    parser.add_argument(
        "-f", nargs='?', const=None, help="full path to file", type=str)
    args = parser.parse_args()
    if args.f is not None:
        plot(args.f)
    else:
        plot(filepath, flipped=flipped, e_bounds=energy_bounds,
             res_types=res_types, output_types=output_types,
             channels=channels_to_plot)