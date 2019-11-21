"""a module to consolidate all functions into one process"""
import flipper
import output_simplifier
import resonance_info
import resonance_plotter
import fitter
import scheme_plot
import utils

import os

Nmax_list = [4, 6]
# files in the same order as Nmax:
phase_shift_list = [
    "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/phase_shift_Nmax4.agr",
    "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/phase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6.agr"
]
eigenphase_shift_list = [
    "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/eigenphase_shift_Nmax4.agr",
    "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/eigenphase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6.agr"
]
ncsmc_dot_out_list = [
    "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/ncsm_rgm_Am2_1_1_Nmax4.out",
    "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/ncsm_rgm_Am2_1_1.out_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6"
]
experiment = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/experiment_Li9.txt"

overall_energies = []
overall_widths = []
overall_channels = []
overall_titles = []


def initial_plots(Nmax, phase_shift, eigenphase_shift, ncsmc_dot_out):
    # ensure files exist and are not empty
    for f in [phase_shift, eigenphase_shift, ncsmc_dot_out, experiment]:
        if not os.path.exists(f):
            raise IOError("file "+f+" does not exist!")
        if not os.path.getsize(phase_shift) > 0:
            raise ValueError("file "+f+" is empty!")

    # flip the files, assuming we don't have to rearrange columns at all
    phase_flipped = flipper.flip(phase_shift)
    eigenphase_flipped = flipper.flip(eigenphase_shift)

    # make simplified output file, and return energies of bound states
    bound_energies, bound_titles = output_simplifier.simplify(ncsmc_dot_out)

    # get info about all resonances in the files, save images, ...
    resonance_info.get_resonance_info(
        phase_flipped, Nmax=Nmax, already_flipped=True)
    resonance_info.get_resonance_info(
        eigenphase_flipped, Nmax=Nmax, already_flipped=True)

    # plot all channels, and make csvs for each individual channel too
    resonance_plotter.plot(phase_flipped, flipped=True, Nmax=Nmax)
    resonance_plotter.plot(eigenphase_flipped, flipped=True, Nmax=Nmax)

    # stuff we'll need later
    return bound_energies, bound_titles, eigenphase_flipped


def select_interesting_channels(Nmax, bound_energies,
                                bound_titles, eigenphase_flipped):
    interesting_channel_file = "resonances_Nmax_{}/interesting.txt".format(Nmax)
    if not os.path.exists(interesting_channel_file):
        # here you have to look at the resonance images,
        # and figure out which ones are interesting.

        # you're looking for phase vs energy curves that look like
        # a sigmoid function, or I guess kind of like a cubic near the bend.

        # When you find those, write down their corresponding lines
        # from the resonances.csv file.

        print("enter all interesting channels in", interesting_channel_file)
        help_str = """
        When you're done, the file should look something like this:

        Eigenphase
        3,+,3,1,strong
        3,+,3,3,strong
        3,+,3,3,strong
        5,-,3,4,none
        5,+,3,4,strong
        Phase
        1,+,3,1,strong
        2,+,3,3,possible
        3,-,3,4,strong
        5,-,3,4,none
        5,+,3,4,strong

        """
        print(help_str)
        open(interesting_channel_file, "a+").close()
        input("Hit enter once you've had enough time to enter the right lines: ")

    with open(interesting_channel_file, "r+") as ch_file:
        lines = ch_file.readlines()

    # remove blanks
    lines = [l for l in lines if l != ""]
    phase_channels = ""
    eigenphase_channels = ""

    mode = ""  # "p" for phase, "e" for eigenphase
    for line in lines:
        print(line)
        if "Eigenphase" in line:
            mode = "e"
        elif "Phase" in line:
            mode = "p"
        elif mode == "e":
            eigenphase_channels += line
        elif mode == "p":
            phase_channels += line

    # merge those lists
    all_str = eigenphase_channels + phase_channels
    all_channels = "\n".join(set(all_str.splitlines()))

    # differently formatted version for later
    channel_titles = [
        "_".join(line.split(",")[:-1]) for line in all_channels.splitlines()]
    return all_channels, channel_titles


def add_resonances(Nmax, eigenphase_flipped, all_channels, channel_titles, bound_energies, bound_titles):
    # now use eigenphase file to find details about resonances

    # now re-plot the interesting ones / make a spaghetti plot with all those
    eigenphase_csvs = resonance_plotter.plot(
        eigenphase_flipped, flipped=True, Nmax=Nmax, channels=all_channels)

    # path to save channel info
    eigenphase_info_path = os.path.join(utils.output_dir.format(Nmax), "eigenphase_info.csv")

    if not os.path.exists(eigenphase_info_path):
        # find the energy of each resonance
        # (i.e. point of highest slope within the "upward swoop")
        eigenphase_widths = []
        eigenphase_energies = []
        for csv in eigenphase_csvs:
            width, energy = fitter.find_resonance(csv)
            eigenphase_widths.append(width)
            eigenphase_energies.append(energy)
        # save that information in files for easy access later
        fitter.save_info(eigenphase_info_path, channel_titles,
                         eigenphase_widths, eigenphase_energies)
    else:
        eigenphase_widths, eigenphase_energies = [], []
        with open(eigenphase_info_path, "r+") as open_csv:
            lines = open_csv.readlines()[1:]
        for line in lines:
            _, width, energy = line.split(",")
            eigenphase_widths.append(width)
            eigenphase_energies.append(energy)

    eigenphase_energies = [float(e) for e in eigenphase_energies]
    eigenphase_widths = [float(e) for e in eigenphase_widths]

    this_nmax_energies = eigenphase_energies + bound_energies
    this_nmax_widths = eigenphase_widths + [0] * len(bound_energies)
    this_nmax_channels = channel_titles + bound_titles
    this_nmax_title = "${}\\hbar\\omega$".format(Nmax)

    overall_energies.append(this_nmax_energies)
    overall_widths.append(this_nmax_widths)
    overall_channels.append(this_nmax_channels)
    overall_titles.append(this_nmax_title)


def add_nmax_data(Nmax_list):
    for i, Nmax in enumerate(Nmax_list):
        print("working on Nmax =", Nmax)
        ps = phase_shift_list[i]
        es = eigenphase_shift_list[i]
        dot_out = ncsmc_dot_out_list[i]
        bound_energies, bound_titles, eigenphase_flipped = initial_plots(
            Nmax, ps, es, dot_out)
        all_channels, channel_titles = select_interesting_channels(
            Nmax, bound_energies, bound_titles, eigenphase_flipped)
        add_resonances(Nmax, eigenphase_flipped, all_channels, channel_titles,
                    bound_energies, bound_titles)


def get_experimental():
    # grab tunl data from file
    with open(experiment, "r+") as expt_file:
        expt_lines = expt_file.readlines()

    thresh = [line for line in expt_lines if "THRESH" in line]
    if len(thresh) != 1:
        raise ValueError("too few / many thresholds!")

    # the THRESH line looks like "THRESH: 3.213\n"
    thresh_num = float(thresh[0].split()[-1].replace("\n", ""))

    expt_energies = []
    expt_widths = []
    expt_channels =  []
    for line in expt_lines:
        try:
            energy, width, J, parity, T = line.split(",")
        except ValueError:
            # if parsing fails, no big deal, that's expected for non-data lines in
            # the file, i.e. the preamble before the e,w,j,p,t lines
            continue
        channel_title = "{}_{}_{}".format(J, parity, T)
        expt_energies.append(float(energy) - thresh_num)
        expt_widths.append(float(width))
        expt_channels.append(channel_title)

    overall_energies.append(expt_energies)
    overall_widths.append(expt_widths)
    overall_channels.append(expt_channels)
    overall_titles.append("Experiment")

add_nmax_data(Nmax_list)
get_experimental()

scheme_plot.plot_multi_levels(
    overall_energies,
    overall_widths,
    overall_channels,
    overall_titles)