"""
A module to consolidate all functions in ncsmc_python, so you can just
feed it the NCSMC output, and it gives you a bunch of useful stuff:

- plots of all resonances
- spaghetti plot with interesting resonances
- level scheme plot
"""
import flipper
import output_simplifier
import resonance_plotter
import fitter
import scheme_plot
import utils

import os

# what resolution to use for final spaghetti + scheme plot images
high_res_dpi = 900

Nmax_list = [4, 6]
# files in the same order as Nmax_list:
file_dir = ""
phase_shift_list = [os.path.join(file_dir, f) for f in [
    "../_Nmax4_ncsmc_output/phase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax4.agr_edited",
    "../_Nmax6_ncsmc_output/phase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6.agr_edited"]
]
eigenphase_shift_list = [os.path.join(file_dir, f) for f in [
    "../_Nmax4_ncsmc_output/eigenphase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax4.agr_edited",
    "../_Nmax6_ncsmc_output/eigenphase_shift_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6.agr_edited"]
]
ncsmc_dot_out_list = [os.path.join(file_dir, f) for f in [
    "../_Nmax4_ncsmc_output/ncsm_rgm_Am2_1_1.out_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax4",
    "../_Nmax6_ncsmc_output/ncsm_rgm_Am2_1_1.out_nLi8_n3lo-NN3Nlnl-srg2.0_20_Nmax6"]
]
experiment = os.path.join(file_dir, "..", "experiment_Li9.txt")
"""
To run process_ncsmc_output.py,
you must have an experiment.txt file stored at the above location.


That file should look something like this:

[start of file]
Data is from the TUNL images and widths are eyeballed
(http://www.tunl.duke.edu/nucldata/figures/09figs/09_03_2004.gif)

States are given in the form
"Energy Width J parity T" but with commas.
Don't want to mess up the parsing by using commas elsewhere!

Li9
THRESH 4.0639
0,0,1.5,-,1.5
2.691,0,0.5,-,?
4.296,0.2,2.5,-,?
5.38,0.4,?,?,?
6.43,0,?,?,?
[end of file]

The stuff at the top of the file isn't necessary, just helpful for a reader.
The program just looks for the THRESH line, and all lines with commas.
Use question marks for values that are not known experimentally.
"""

# stop editing here unless you want to change program behaviour

overall_energies = []
overall_widths = []
overall_channels = []
overall_titles = []

help_str = """
First, take a look at the PNGs_phase files, to figure out which
channels are interesting

(just look at the graph, if you see a swoop up, it's interesting)

Then, figure out which columns in the eigenphase file those match with.
(they should have the same J, pi, T, but may have a different column #)

Then, open up resonances_eigenphase_Nmax_[#].csv and copy the lines
associated with those channels.

When you're done, the file should look
something like this:

3,+,3,1,strong
3,+,3,3,strong
3,-,3,3,strong
5,-,3,4,none
5,+,3,4,strong

[lines copied from the eigenphase csv file, one blank line at the end]

"""
"""
``help_str`` is the help text displayed to the user when they have to look
at the phase shift plots and select which channels are important.

Note that it looks a whole lot better in the python file than online.
"""


def select_interesting_channels(Nmax):
    """
    Get interesting channels (i.e. those channels which contain resonances)
    by using human input in a file.

    Nmax:
        float
    """
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
        print(help_str)
        open(interesting_file, "a+").close()
        input("Hit enter once you've had enough time to enter the right " +
              "lines. Don't forget to SAVE the file!")

    with open(interesting_file, "r+") as ch_file:
        channels_str = ch_file.read()

    # differently formatted version for use as titles
    channel_titles = [
        "_".join(line.split(",")[:-1]) for line in channels_str.splitlines()]

    return channels_str, channel_titles


def add_resonances(Nmax, eigenphase_flipped, channels_str, channel_titles,
                   bound_energies, bound_titles):
    """
    Use eigenphase file to add details about resonances (widths, energies, ...)
    to the overall lists of data to be plotted.

    Nmax:
        float

    eigenphase_flipped:
        path to flipped eigenphase file

    channels_str:
        string, the contents of the csv file with the details
        of interesting resonances (width, energy, state)

    channel_titles:
        list of strings, again representing channels but formatted nicely

    bound_energies:
        list of floats, energies of bound states

    bound_titles:
        list of strings, titles of bound states
    """

    # plot interesting resonances / spaghetti plot, in high-res
    eigenphase_csvs = resonance_plotter.plot(
        eigenphase_flipped, flipped=True, Nmax=Nmax,
        channels=channels_str, dpi=high_res_dpi)

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
    this_nmax_title = "${}\\hbar\\Omega$".format(Nmax)

    overall_energies.append(this_nmax_energies)
    overall_widths.append(this_nmax_widths)
    overall_channels.append(this_nmax_channels)
    overall_titles.append(this_nmax_title)


def add_nmax_data(Nmax_list):
    """
    Add data to be plotted on the level scheme for each Nmax in Nmax_list

    Nmax_list:
        list of floats
    """
    for i, Nmax in enumerate(Nmax_list):
        print("working on Nmax =", Nmax)
        # get ncsmc, .out output files
        ps = phase_shift_list[i]
        es = eigenphase_shift_list[i]
        dot_out = ncsmc_dot_out_list[i]
        # flip phase files
        ps = flipper.flip(ps, verbose=False)
        es = flipper.flip(es, verbose=False)
        # make low-res plots
        resonance_plotter.plot(ps, flipped=True, Nmax=Nmax)
        resonance_plotter.plot(es, flipped=True, Nmax=Nmax)

        # get bound state info
        bound_energies, bound_titles = output_simplifier.simplify(dot_out)

        # select interesting channels, i.e. those with resonances
        channels_str, channel_titles = select_interesting_channels(Nmax)
        # stick those channels in the overall plot
        add_resonances(Nmax, es, channels_str, channel_titles,
                       bound_energies, bound_titles)


def get_experimental():
    """
    Grab experimental data from a file which must be prepared in advance.

    The path to the file is saved above as ``experiment``
    """
    with open(experiment, "r+") as expt_file:
        expt_lines = expt_file.readlines()

    thresh = [line for line in expt_lines if "THRESH" in line]
    if len(thresh) != 1:
        raise ValueError("too few / many thresholds!")

    # the THRESH line looks like "THRESH: 3.213\n"
    thresh_num = float(thresh[0].split()[-1].replace("\n", ""))

    expt_energies = []
    expt_widths = []
    expt_channels = []
    for line in expt_lines:
        try:
            energy, width, J, parity, T = line.split(",")
        except ValueError:
            # if parsing fails, no big deal, that's expected for non-data
            # lines in the file, i.e. the preamble before the e,w,j,p,t lines
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
    """
    Plot a level scheme! Grab all data and call
    ``scheme_plot.plot_multi_levels()``
    """
    # first ensure files exist
    files = (phase_shift_list + eigenphase_shift_list +
             ncsmc_dot_out_list + [experiment])
    for f in files:
        if not os.path.exists(f):
            raise OSError("file {} does not exist!".format(f))
        if not os.path.getsize(f) > 0:
            raise ValueError("file "+f+" is empty!")

    # then get the data we need
    add_nmax_data(Nmax_list)
    get_experimental()

    # then plot the level scheme
    scheme_plot.plot_multi_levels(
        overall_energies,
        overall_widths,
        overall_channels,
        overall_titles)


if __name__ == "__main__":
    plot_scheme()
