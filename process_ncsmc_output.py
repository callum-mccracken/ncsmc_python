"""a module to consolidate all functions into one process"""
import flipper
import output_simplifier
import resonance_info
import resonance_plotter
import fitter
import scheme_plot
import utils

import os

# what resolution to use for final images
high_res_dpi = 900

Nmax_list = [4, 6]
# files in the same order as Nmax_list:
file_dir = ""
phase_shift_list = [os.path.join(file_dir, f) for f in [
    "Nmax4/phase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax4.agr_edited",
    "Nmax6/phase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6.agr_edited"]
]
eigenphase_shift_list = [os.path.join(file_dir, f) for f in [
    "Nmax4/eigenphase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax4.agr_edited",
    "Nmax6/eigenphase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6.agr_edited"]
]
ncsmc_dot_out_list = [os.path.join(file_dir, f) for f in [
    "Nmax4/ncsm_rgm_Am2_1_1.out_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax4",
    "Nmax6/ncsm_rgm_Am2_1_1.out_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6"]
]
experiment = os.path.join(file_dir, "experiment_Li9.txt")

for f in phase_shift_list+eigenphase_shift_list+ncsmc_dot_out_list+[experiment]:
    if not os.path.exists(f):
        raise OSError("file {} does not exist!".format(f))
    if not os.path.getsize(f) > 0:
            raise ValueError("file "+f+" is empty!")

overall_energies = []
overall_widths = []
overall_channels = []
overall_titles = []


def select_interesting_channels(Nmax):
    interesting_file = "resonances_Nmax_{}/interesting.txt".format(Nmax)
    exists = os.path.exists(interesting_file)
    blank = True if not exists else os.path.getsize(interesting_file) == 0
    must_write = (not exists) or blank

    if must_write:
        # here you have to look at the resonance images,
        # and figure out which ones are interesting.

        # you're looking for phase vs energy curves that look like
        # a sigmoid function, or I guess kind of like a cubic near the bend.

        # When you find those, write down their corresponding lines
        # from the resonances.csv file.

        print("Enter all interesting channels in", interesting_file)
        help_str = """
        When you're done, the file should look
        something like this:

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
        open(interesting_file, "a+").close()
        input("Hit enter once you've had enough time to enter the right lines: ")

    with open(interesting_file, "r+") as ch_file:
        lines = ch_file.readlines()

    # remove blanks
    lines = [l for l in lines if l != ""]
    phase_channels = ""
    eigenphase_channels = ""

    mode = ""  # "p" for phase, "e" for eigenphase
    for line in lines:
        if "Eigenphase" in line:
            mode = "e"
        elif "Phase" in line:
            mode = "p"
        elif mode == "e":
            eigenphase_channels += line
        elif mode == "p":
            phase_channels += line

    # merge those lists
    channels_str = "\n".join(set(
        (eigenphase_channels + phase_channels).splitlines()))

    # differently formatted version for later
    channel_titles = [
        "_".join(line.split(",")[:-1]) for line in channels_str.splitlines()]

    return channels_str, channel_titles


def add_resonances(Nmax, eigenphase_flipped, channels_str, channel_titles,
                   bound_energies, bound_titles):
    """use eigenphase file to find details about resonances"""

    # plot interesting resonances / spaghetti plot with only those, in high-res
    eigenphase_csvs = resonance_plotter.plot(eigenphase_flipped,
        flipped=True, Nmax=Nmax, channels=channels_str, dpi=high_res_dpi)

    # save channel info if needed
    eigenphase_info_path = os.path.join(
        utils.output_dir.format(Nmax), "eigenphase_info.csv")
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

    # grab energy / width of resonances from file
    eigenphase_titles, eigenphase_widths, eigenphase_energies = [], [], []
    with open(eigenphase_info_path, "r+") as open_csv:
        lines = open_csv.readlines()[1:]  # first entry is a title
    for line in lines:
        title, width, energy = line.split(",")
        eigenphase_widths.append(width)
        eigenphase_energies.append(energy)
        eigenphase_titles.append(title)

    eigenphase_energies = [float(e) for e in eigenphase_energies]
    eigenphase_widths = [float(e) for e in eigenphase_widths]

    this_nmax_energies = eigenphase_energies + bound_energies
    this_nmax_widths = eigenphase_widths + [0] * len(bound_energies)
    this_nmax_channels = eigenphase_titles + bound_titles
    this_nmax_title = "${}\\hbar\\omega$".format(Nmax)

    overall_energies.append(this_nmax_energies)
    overall_widths.append(this_nmax_widths)
    overall_channels.append(this_nmax_channels)
    overall_titles.append(this_nmax_title)


def add_nmax_data(Nmax_list):
    for i, Nmax in enumerate(Nmax_list):
        print("working on Nmax =", Nmax)
        # get ncsmc output files
        ps = phase_shift_list[i]
        es = eigenphase_shift_list[i]
        # flip them
        ps = flipper.flip(ps)
        es = flipper.flip(es)
        # make plots
        resonance_plotter.plot(ps, flipped=True, Nmax=Nmax)
        resonance_plotter.plot(es, flipped=True, Nmax=Nmax)

        # get output file which contains bound states
        dot_out = ncsmc_dot_out_list[i]
        # get bound state info and flipped ephase file name
        bound_energies, bound_titles = output_simplifier.simplify(dot_out)

        # select interesting channels, i.e. those with resonances
        channels_str, channel_titles = select_interesting_channels(Nmax)
        # stick those channels in the overall plot
        add_resonances(Nmax, es, channels_str, channel_titles,
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
    print("got experimental data")

def plot_scheme():
    add_nmax_data(Nmax_list)
    get_experimental()

    scheme_plot.plot_multi_levels(
        overall_energies,
        overall_widths,
        overall_channels,
        overall_titles)

plot_scheme()