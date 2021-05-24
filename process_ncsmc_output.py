"""
A module to consolidate all functions in ncsmc_python, so you can just
feed it the NCSMC output, and it gives you a bunch of useful stuff:

- plots of all resonances
- spaghetti plot with interesting resonances
- level scheme plot
"""

import os

# what resolution to use for final spaghetti + scheme plot images
high_res_dpi = 900

Nmax_list = [7]
# files in the same order as Nmax_list:
file_dir = "/home/callum/Documents/Undergrad Work/npsm/input_files/"
put_output_in_file_dir = True  # otherwise defaults to dir with python files
phase_shift_list = [os.path.join(file_dir, f) for f in [
    "phase_shift.agr"]
]
eigenphase_shift_list = [os.path.join(file_dir, f) for f in [
    "eigenphase_shift.agr"]
]
ncsmc_dot_out_list = [os.path.join(file_dir, f) for f in [
    "ncsm_rgm_Am2_1_1.out"]
]
experiment = os.path.join(file_dir, "", "experiment_C10.txt")

# by default we only make plots of eigenphase, do you want phase plots too?
make_phase_plots_too = True
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

# write config file
conf_file = os.path.join(os.path.dirname(__file__), "config.txt")
if put_output_in_file_dir:
    with open(conf_file, "w") as conf:
        conf.write(file_dir)

# import a bunch of stuff
# I know it's not normal to import here but these files need the config file
# or they'll default to the old storage location
import flipper
import output_simplifier
import resonance_plotter
import fitter
import scheme_plot
import utils

# remove config file
if os.path.exists(conf_file):
    os.remove(conf_file)

overall_energies = []
overall_widths = []
overall_channels = []
overall_titles = []

eigen_help_str = """
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
``eigen_help_str`` is the help text displayed to the user when they have to
look at the phase shift plots and select which channels are important.

Note that it looks a whole lot better in the python file than online.
"""

phase_help_str = """
You have opted to plot (non-eigen)phase data too,
by setting make_phase_plots_too = True.

Take a look at the PNGs_phase files, to figure out which
channels are interesting

(just look at the graph, if you see a swoop up, it's interesting)

Then, open up resonances_phase_Nmax_[#].csv and copy the lines
associated with those channels.

When you're done, the file should look
something like this:

3,+,3,1,strong
3,+,3,3,strong
3,-,3,3,strong
5,-,3,4,none
5,+,3,4,strong

[lines copied from the phase csv file, one blank line at the end]

"""
"""
``phase_help_str`` is just like ``eigen_help_str``, but for phase plots.
"""


def select_interesting_channels(Nmax):
    """
    Get interesting channels (i.e. those channels which contain resonances)
    by using human inputs in files.

    Nmax:
        float
    """
    eigenphase_interesting_file = os.path.join(
        utils.output_dir.format(Nmax), "interesting.txt")
    eigen_exists = os.path.exists(eigenphase_interesting_file)
    eigen_blank = (True if not eigen_exists
                   else os.path.getsize(eigenphase_interesting_file) == 0)
    eigen_must_write = (not eigen_exists) or eigen_blank

    if eigen_must_write:
        # here you have to look at the resonance images,
        # and figure out which ones are interesting.

        # you're looking for phase vs energy curves that look like
        # a sigmoid function, or I guess kind of like a cubic near the bend.

        # When you find those, write down their corresponding lines
        # from the resonances.csv file.

        print("Enter all interesting channels in", eigenphase_interesting_file)
        print(eigen_help_str)
        open(eigenphase_interesting_file, "a+").close()
        input("Hit enter once you've had enough time to enter the right " +
              "lines. Don't forget to SAVE the file!")

    with open(eigenphase_interesting_file, "r+") as eigen_ch_file:
        eigen_channels_str = eigen_ch_file.read()

    # differently formatted version for use as titles
    eigen_channel_titles = [
        "_".join(line.split(",")[:-1])
        for line in eigen_channels_str.splitlines()]

    if make_phase_plots_too:
        phase_interesting_file = os.path.join(
            utils.output_dir.format(Nmax), "interesting_phase.txt")
        phase_exists = os.path.exists(phase_interesting_file)
        phase_blank = (True if not phase_exists
                       else os.path.getsize(phase_interesting_file) == 0)
        phase_must_write = (not phase_exists) or phase_blank

        if phase_must_write:
            print("Enter all interesting channels in", phase_interesting_file)
            print(phase_help_str)
            open(phase_interesting_file, "a+").close()
            input("Hit enter once you've had enough time to enter the right " +
                  "lines. Don't forget to SAVE the file!")

        with open(phase_interesting_file, "r+") as phase_ch_file:
            phase_channels_str = phase_ch_file.read()

    else:
        phase_channels_str = None

    return eigen_channels_str, eigen_channel_titles, phase_channels_str


def add_resonances(Nmax,
                   eigenphase_flipped, eigen_channels_str,
                   eigen_channel_titles,
                   phase_flipped, phase_channels_str,
                   bound_energies, bound_titles):
    """
    Use eigenphase file to add details about resonances (widths, energies, ...)
    to the overall lists of data to be plotted.

    Also takes phase data for plotting purposes if needed

    Nmax:
        float

    eigenphase_flipped:
        path to flipped eigenphase file

    eigen_channels_str:
        string, the contents of the csv file with the details
        of interesting resonances (width, energy, state)

    eigen_channel_titles:
        list of strings, again representing channels but formatted nicely

    phase_flipped, phase_channels_str:
        Same idea as all the eigen ones but for phase.
        Last one may be None.

    bound_energies:
        list of floats, energies of bound states

    bound_titles:
        list of strings, titles of bound states
    """

    # plot interesting resonances / spaghetti plot, in high-res
    eigenphase_csvs = resonance_plotter.plot(
        eigenphase_flipped, flipped=True, Nmax=Nmax,
        channels=eigen_channels_str, dpi=high_res_dpi)

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
        fitter.save_info(eigenphase_info_path, eigen_channel_titles,
                         eigenphase_widths, eigenphase_energies)

    if make_phase_plots_too:
        resonance_plotter.plot(
            phase_flipped, flipped=True, Nmax=Nmax,
            channels=phase_channels_str, dpi=high_res_dpi)
        # we don't need widths and energies for phase plots

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

        # make unflipped plots, flipped=True prevents flipping
        resonance_plotter.plot(
            ps, flipped=True, Nmax=Nmax, suffix='_unflipped')
        resonance_plotter.plot(
            es, flipped=True, Nmax=Nmax, suffix='_unflipped')

        # flip phase files
        ps = flipper.flip(ps, verbose=False)
        es = flipper.flip(es, verbose=False)

        # make flipped plots
        resonance_plotter.plot(ps, flipped=True, Nmax=Nmax)
        resonance_plotter.plot(es, flipped=True, Nmax=Nmax)

        # get bound state info
        bound_energies, bound_titles = output_simplifier.simplify(dot_out)

        # select interesting channels, i.e. those with resonances
        # eigen_channels_string, eigen_channels_titles, phase_channels_string
        # just shortened so the line wasn't weirdly long
        e_ch_str, e_ch_titles, p_ch_str = select_interesting_channels(Nmax)
        # stick those channels in the overall plot
        add_resonances(Nmax, es, e_ch_str, e_ch_titles,
                       ps, p_ch_str,
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
            energy, width, J, parity, T = line.strip("\n").split(",")
            if width == "?":
                width = "0"
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
