"""
Contains a function for making plots related to ncsmc output.

Makes both matplotlib (png and svg) and xmgrace plots

Can be run with

python resonance_plotter.py -f /path/to/some/file (assumes file is not flipped)

It will:
- flip the file (output saved in same directory as original file)
- detect which channels have resonances (saved in resonances directory)
- plot all channels

"""
from os.path import join, exists
import os
from math import inf
import argparse

import matplotlib.pyplot as plt

import utils
import flipper
from resonance_info import get_resonance_info

# File path (relative paths are okay)
filepath = "/path/to/phase_shift.agr_flipped"

# value of Nmax, for file naming purposes
Nmax = 4

# Has the file already been "flipped"?
flipped = True

# Which channels should be added to the multi channel plot?
# format: 2J,parity,2T,column_number,resonance_type
# e.g.: "2,+,4,1,strong"
# blank lines are okay, but no extra spacing please!
# (just paste into the space between the pair of triple quotes)
channels_to_plot = """

"""

# Controls what bounds to use for energy axis,
# e.g. if you have 0-10 but only want 0-5, set this to (0, 5)
# If you don't want bounds set this to (-inf, inf)
energy_bounds = (-inf, inf)

# types of resonances to plot. Possible values: "strong", "possible", "none"
# res_types = ["strong"]  # if you just want "strong" resonances
res_types = "all"  # if you want to plot everything

# resolution of png images, dots per inch
dpi = 90


def plot(filename, flipped=False, e_bounds=(-inf, inf), res_types="all",
         channels="", Nmax=None, dpi=dpi):
    """
    Makes a whole bunch of plots.
    - one for each of the user-specified channels
    - one with all channels on the same plot
    """
    if res_types == "all":
        res_types = ["strong", "possible", "none"]

    filename = utils.abs_path(filename)
    phase_word = "eigenphase" if "eigen" in filename else "phase"

    # ensure file is flipped
    if flipped:
        new_filename = filename
    else:
        new_filename = flipper.flip(filename)

    # if channels are provided, there will be at least one number in the string
    # if no channels are provided, get them all
    if not any([utils.is_float(char) for char in channels]):
        file_suffix = "auto"
        # get csv filename with resonance info
        res_output_file = get_resonance_info(
            filename, Nmax=Nmax, already_flipped=True)
        # take all channels, i.e. all text in the file
        with open(res_output_file, "r+") as channel_file:
            channels = channel_file.read()
    else:
        file_suffix = "custom"

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

    # all_channels: dict, key = title, value = list of phases for that channel
    # energies: a list of energy values, possibly longer than some channels
    all_channels, energies = flipper.separate_into_channels(new_filename)

    # if energy bounds are -inf, inf, let's set them to the min / max e values
    if e_bounds == (-inf, inf):
        l_bound, r_bound = min(energies), max(energies)
    else:
        l_bound, r_bound = e_bounds

    output_dir = utils.output_dir.format(Nmax)
    if not exists(output_dir):
        os.mkdir(output_dir)
    png_dir = join(output_dir, "PNGs_"+phase_word)
    csv_dir = join(output_dir, "CSVs_"+phase_word)
    grace_dir = join(output_dir, "grace_files_"+phase_word)
    for d in [png_dir, csv_dir, grace_dir]:
        if not exists(d):
            os.mkdir(d)

    print("Working on resonance plotting")
    main_xmgrace_string = ""  # xmgrace string for the full file
    channel_string = ""  # xmgrace string for each individual channel
    series_counter = 0  # xmgrace series titles
    csv_paths = []  # list of csv files of channels we plot

    # now look in each channel, plot the ones we care about
    to_plot = []
    for title, phases in all_channels.items():
        # see if the title matches one we were given. If so, plot
        nice_title = utils.make_nice_title(title)
        if nice_title in input_titles:
            print("adding", nice_title, "to plot\r", end="")
            # energies may be longer than phases,
            # so we truncate energy where needed
            len_diff = len(energies) - len(phases)
            if len_diff != 0:
                trunc_energies = energies[len_diff:]
            else:
                trunc_energies = energies
            # then only plot within the given bounds
            plot_energies, plot_phases = [], []
            for e, p in zip(trunc_energies, phases):
                if l_bound <= e and e <= r_bound:
                    plot_energies.append(e)
                    plot_phases.append(p)

            # make a matplotlib channel plot
            channel_fig, channel_ax = plt.subplots()
            plot_title = utils.make_plot_title(nice_title)
            channel_ax.set_title(plot_title)
            channel_ax.set_ylabel("Phase (degrees)")
            # nothing interesting should happen outside this range, right?
            # I'd let matplotlib autogenerate the graph limits,
            # but then you get graphs with a range of -1 to 1, which have
            # an interesting shape but are not large enough to be useful
            channel_ax.set_ylim(-50, 200)
            channel_ax.set_xlim(l_bound, r_bound)
            channel_ax.set_xlabel("Energy (MeV)")
            channel_ax.plot(plot_energies, plot_phases)
            channel_path = join(
                png_dir,
                phase_word+"_"+nice_title+"_Nmax_"+str(Nmax)+".png")
            channel_fig.savefig(channel_path, dpi=dpi)
            plt.close(channel_fig)
            to_plot.append((plot_energies, plot_phases, plot_title))

            # make xmgrace file for channel
            c_title = utils.xmgrace_title(title, series_counter) + "\n"
            channel_string = c_title
            series_counter += 1
            for e, p in zip(plot_energies, plot_phases):
                channel_string += str(e) + " " + str(p) + "\n"
            channel_string += "&\n"
            # append it to the full file string
            main_xmgrace_string += channel_string
            # and also save it as its own file with series number = 0
            lines = channel_string.splitlines()
            lines[0] = utils.xmgrace_title(lines[0], 0)
            channel_string = "\n".join(lines)
            grdt_name = join(
                grace_dir,
                phase_word+"_"+nice_title+"_Nmax_"+str(Nmax)+".grdt")
            with open(grdt_name, "w+") as channel_file:
                channel_file.write(channel_string)

            # make csv file for channel too
            csv_path = join(
                csv_dir,
                phase_word+"_"+nice_title+"_Nmax_"+str(Nmax)+".csv")
            with open(csv_path, "w+") as csv_file:
                for e, p in zip(plot_energies, plot_phases):
                    csv_file.write(",".join([str(e), str(p)]) + "\n")
            csv_paths.append(csv_path)

    # make main matplotlib plot
    print("Scopping out a bowl of spaghetti...\r", end="")
    plt.cla()
    plt.clf()
    plt.title("Multi-Channel "+phase_word.title()+" Shifts")
    plt.ylabel("Phase (degrees)")
    plt.ylim(-50, 200)
    plt.xlim(l_bound, r_bound)
    plt.xlabel("Energy (MeV)")
    for energy, phase, title in to_plot:
        plt.plot(energy, phase, label=title)
    main_mpl_path = join(
        png_dir,
        phase_word+"_Nmax_"+str(Nmax)+"_"+file_suffix+".png")
    plt.legend(loc='lower right', shadow=False, fontsize='xx-small')
    plt.savefig(main_mpl_path, dpi=dpi)
    plt.savefig(main_mpl_path.replace(".png", ".svg"))
    plt.close()

    # make main xmgrace file
    main_grdt_path = join(
        grace_dir,
        phase_word+"_plot_Nmax_"+str(Nmax)+"_"+file_suffix+".grdt")
    with open(main_grdt_path, "w+") as grace_file:
        grace_file.write(main_xmgrace_string)

    print("Done plotting! Saved main plot(s) to:")
    print(main_mpl_path)
    print(main_grdt_path)

    # return paths to csv files of channels we plotted
    return csv_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Resonance Plotter")
    parser.add_argument("-f", nargs='?', const=None, help="filepath", type=str)
    args = parser.parse_args()
    if args.f is not None:
        plot(args.f)
    else:
        plot(filepath, flipped=flipped, e_bounds=energy_bounds,
             res_types=res_types, channels=channels_to_plot)
