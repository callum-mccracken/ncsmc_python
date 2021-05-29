"""
A module with functions for making plots of level schemes,
manually (for once you have your data but just want to plot it).

Either single or multi-scheme plots are possible, and we make output in
two different formats.

The one with a .png extension is a standard image file

The one with a .svg extension is also an image file, but saved in
Scalable Vector Graphics format, which means it is more easily editable.
To open / edit that file, may I recommend `Inkscape <https://inkscape.org/>`_?

"""

import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator

import utils

mpl.rcParams['lines.linewidth'] = '10'
mpl.rcParams['axes.linewidth'] = '10'
mpl.rcParams['lines.dashed_pattern'] = (7, 2)
mpl.rcParams['lines.dotted_pattern'] = (1, 1.65)
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.weight"] = "bold"
plt.rc('text', usetex=True)
plt.rc('font', size=16)
# general plot formatting
plt.style.use('seaborn-white')


axis_label_size = 50

# we'll pick colors from this list
# green blue red
colors = ['#7FC97F', '#2E9EDE', '#F80C00', None, None]

cmap = plt.get_cmap('viridis')

dpi_high_res = 200

# dimensions of individual spectrum plots
x_size = 5
y_size = 7

# x axis bounds, definitely don't change these unless you're feeling rebellious
min_x = 0
max_x = 10

energies_list = [
    [-2.76, -0.98, 0.90, 1.82, 2.79],
    [-2.94, -1.09, 0.69, 1.53, 2.30],
    [-2.81, -1.14, 0.67, 1.41, 2.65],
    [-4.07, -1.37, 0.23, 1.37, 2.62],
    [-4.06, -1.37, 0.23, 1.32, 2.62],
]

widths_list = [
    [0, 0, 1.04, 1.16, 5.11],
    [0, 0, 0.66, 0.75, 3.91],
    [0, 0, 0.56, 0.59, 2.50],
    [0, 0, 0.11, 0.61, 2.50],
    [0, 0, 0.10, 0.60, 0.00],
]

# strings of the form ``J_parity_T[_column]`` (the _column is optional).
channel_title_list = [
    ["1.5_-_1.5", "1.5_-_1.5", "2.5_-_1.5", "0.5_-_1.5", "1.5_-_1.5"],
    ["1.5_-_1.5", "1.5_-_1.5", "2.5_-_1.5", "0.5_-_1.5", "1.5_-_1.5"],
    ["1.5_-_1.5", "1.5_-_1.5", "2.5_-_1.5", "0.5_-_1.5", "1.5_-_1.5"],
    ["1.5_-_1.5", "1.5_-_1.5", "2.5_-_1.5", "0.5_-_1.5", "1.5_-_1.5"],
    ["?_?_?", "?_?_?", "2.5_-_?", "0.5_-_?", "1.5_-_1.5"],
]

main_title_list = [
    "$4\\hbar\\Omega$",
    "$6\\hbar\\Omega$",
    "$8\\hbar\\Omega$",
    "$8\\hbar\\Omega$ $\\textrm{Pheno}$",
    "$\\textrm{Experiment}$",
]

def linewidth_from_data_units(linewidth, axis, reference='y'):
    """
    Convert a linewidth in data units to linewidth in points.
    (many thanks to stack exchange!)

    linewidth:
        float, how big you want your line to be, in data units

    axis:
        axis object on which your graph is made

    reference:
        string, x or y, which axis data units?
    """

    fig = axis.get_figure()
    if reference == 'x':
        length = fig.bbox_inches.width * axis.get_position().width
        value_range = np.diff(axis.get_xlim())
    elif reference == 'y':
        length = fig.bbox_inches.height * axis.get_position().height
        value_range = np.diff(axis.get_ylim())
    # Convert length to points
    length *= 72
    # Scale linewidth to value range
    return linewidth * (length / value_range)


def plot_levels(energies, widths, channel_titles, main_title,
                min_y, max_y, ax=None, y_label="E [MeV]",
                colors=None):
    """
    Makes a plot of a single level scheme.

    energies:
        list of floats, energies to plot

    widths:
        list of floats, widths to plot

    channel_titles:
        list of strings, text to be placed beside levels

    main_title:
        main plot title, usually something like 2\\hbar\\Omega

    min_y, max_y:
        two floats, if a width would go outside these bounds, we cut it off

    ax:
        matplotlib axis object on which we wish to make this plot.
        If you're just making a single plot there's no need to worry about this
        it's just useful if you're putting multiple ones on the same figure.

    y_label:
        string, label for the y axis

    colors:
        colors for each level's width, in any matplotlib-compatible format

    """
    # set up plot
    if ax is None:
        _, ax = plt.subplots(figsize=(x_size, y_size))

    # Add titles
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(3)
    ax.set_title(
        "{}".format(main_title), loc='center', pad=15,
        fontsize=axis_label_size, fontweight=20, color='black', fontname='Times New Roman')
    ax.set_xlabel("")
    ax.set_ylabel(y_label, fontsize=axis_label_size, fontname='Times New Roman')
    ax.set_xticks([])
    ax.yaxis.set_minor_locator(MultipleLocator(0.25))
    ax.yaxis.set_major_locator(MultipleLocator(2))
    ax.tick_params(axis="y", which='both', left=True, right=False, labelsize=50)
    ax.tick_params(which='both', direction='in', length=18, width=3)
    ax.tick_params(which='minor', length=9, width=2)
    x = np.linspace(min_x, 0.7*max_x, num=len(energies), endpoint=True).tolist()
    x_inc = x[1] - x[0]

    # plot dotted line at zero energy
    ax.plot([min_x-5, max_x+5], [0, 0], 'k--', linewidth=3,
            solid_capstyle="butt", alpha=0.3, dashes=(2,2))

    # plot each energy line with a bar around it depending on width
    # also add titles for energy, state label, width
    energies = np.array(energies)
    widths = np.array(widths)
    idx = list(reversed(np.argsort(energies)))
    energies = energies[idx]
    widths = widths[idx]
    # e_titles = [e_titles[i] for i in idx]
    channel_titles = [channel_titles[i] for i in idx]

    for i in range(len(energies)):
        # make an initial skinny plot for each energy value
        ax.plot(x, [energies[i]]*len(x),
                marker='', color='k', linewidth=3, alpha=1,
                solid_capstyle="butt")

        # figure out if this energy's width will fit on the plot
        top = energies[i] + widths[i] / 2
        btm = energies[i] - widths[i] / 2

        # x value of the middle of this point
        x_mid = 1.15 * (x[i] + x_inc / 2) + 0.4

        if energies[i] < 0:  # bound state
            ax.plot(x, [energies[i]]*len(x), marker='', color="black",
                    linewidth=1, alpha=1, solid_capstyle="butt")
        else:  # typical resonance where the width bars will fit
            x_width = 1.5*linewidth_from_data_units(x_inc, ax, reference="x")
            ax.plot([x_mid, x_mid], [top, btm], marker='', color=colors[i],
                    linewidth=x_width, alpha=1, solid_capstyle='butt')
        
        # state info (J, pi, T, in the form J^p T) title
        plot_title = utils.plot_title_2(channel_titles[i])
        ax.text(9, energies[i]+0.4, plot_title,
                horizontalalignment='center', fontsize=40, color='black',
                verticalalignment='center')

def plot_multi_levels(energies_list, widths_list, channel_title_list,
                      main_title_list):
    """
    Make plots of many different schemes, stiched together into one figure.

    energies_list:
        list of list of floats, energies of each channel on each plot

    widths_list:
        list of list of floats, widths of each channel on each plot

    channel_title_list:
        list of list of strings, titles of each channel on each plot

    main_title_list:
        list of strings, main titles of each plot
    """
    n_spectra = len(energies_list)
    n_lines = max([len(e) for e in energies_list])

    # make main figure
    _, axes = plt.subplots(
        nrows=1, ncols=n_spectra, sharex=True, sharey=True,
        figsize=(x_size*n_spectra, y_size))
    if type(axes) != np.ndarray:
        axes = [axes]

    max_energy = max([max(e) for e in energies_list])
    min_energy = min([min(e) for e in energies_list])

    # we'll cut the resonance widths off depending on "factor"
    factor = 0.2
    max_y = max_energy + factor * abs(max_energy-min_energy)
    min_y = min_energy - factor * abs(max_energy-min_energy)
    # plot each individual spectrum
    for ax, e, w, ct, mt in zip(axes, energies_list, widths_list,
                                channel_title_list, main_title_list):
        plot_levels(
            e, w, ct, mt, min_y, max_y, ax=ax, y_label="", colors=colors)

    # set x limits
    plt.xlim(min_x-1, max_x+1)
    # set y limits
    plt.ylim(-4.5, 5)

    # put title only on the first one
    axes[0].set_ylabel("$E$ $\\textrm{[MeV]}$", fontsize=axis_label_size)

    # then save the plot
    if not os.path.exists("level_schemes"):
        os.mkdir("level_schemes")
    fig_path = os.path.join("level_schemes", "level_scheme")
    plt.tight_layout()
    plt.savefig(fig_path+".png", dpi=dpi_high_res)
    plt.savefig(fig_path+".svg")
    plt.savefig(fig_path+".pdf")
    print("Saved level scheme plot as", fig_path+".png")

plot_multi_levels(energies_list, widths_list, channel_title_list, main_title_list)
