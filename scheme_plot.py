"""
A module with functions for making plots of level schemes.

Either single or multi-scheme plots are possible, and we make output in
two different formats.

The one with a .png extension is an image file
(if you haven't heard of png, get outta here).

The one with a .svg extension is also an image file, but saved in
Scalable Vector Graphics format. It's like .agr, but more commonly used.
To open / edit that file, may I recommend `Inkscape <https://inkscape.org/>`_?

"""


import matplotlib.pyplot as plt
import numpy as np
import os
import utils

# general plot formatting
plt.style.use('seaborn-white')

# we'll pick colours from this colormap
cmap = plt.get_cmap('viridis')

dpi = 96
dpi_high_res = 900

# dimensions of spectrum plots, probably don't change these
x_size = 5
y_size = 10

# x axis bounds, definitely don't change these unless you're feeling rebellious
min_x = 0
max_x = 10


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
                min_y, max_y, ax=None, y_label="Energy ($MeV$)",
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
        _, ax = plt.subplots(figsize=(x_size, y_size), dpi=dpi)

    # get colors for spectra if they're not given
    if colors is None:
        colors = cmap(np.linspace(0, 1, len(energies)))

    # Add titles
    ax.set_title(
        "{}".format(main_title), loc='center',
        fontsize=12, fontweight=2, color='black')
    ax.set_xlabel("")
    ax.set_ylabel(y_label)
    ax.set_xticks([])

    x = np.linspace(min_x, max_x, num=len(energies)+1, endpoint=True).tolist()
    x_inc = x[1] - x[0]

    # format energies for plotting
    e_titles = ["{}".format(e) for e in energies]

    # plot dotted line at zero energy
    ax.plot([min_x-5, max_x+5], [0, 0], '--k', linewidth=1,
            solid_capstyle="butt")

    # plot each energy line with a bar around it depending on width
    # also add titles for energy, state label, width
    energies = np.array(energies)
    widths = np.array(widths)
    idx = list(reversed(np.argsort(energies)))
    energies = energies[idx]
    widths = widths[idx]

    for i in range(len(energies)):
        # make an initial skinny plot for each energy value
        ax.plot(x, [energies[i]]*len(x),
                marker='', color='k', linewidth=1, alpha=1,
                solid_capstyle="butt")

        # figure out if this energy's width will fit on the plot
        top = energies[i] + widths[i] / 2
        btm = energies[i] - widths[i] / 2
        itll_fit = top < max_y and btm > min_y

        # x value of the middle of this point
        x_mid = x[i] + x_inc / 2

        if energies[i] < 0:  # bound state
            ax.plot(x, [energies[i]]*len(x), marker='', color="black",
                    linewidth=1, alpha=1, solid_capstyle="butt")
        elif itll_fit:  # typical resonance where the width bars will fit
            x_width = 0.9*linewidth_from_data_units(x_inc, ax, reference="x")
            ax.plot([x_mid, x_mid], [top, btm], marker='', color=colors[i],
                    linewidth=x_width, alpha=0.7, solid_capstyle='butt')
        else:  # if width is too huge to put on the plot, make it a red line
            ax.plot(x, [energies[i]]*len(x), marker='', color="red",
                    linewidth=5, alpha=0.5, solid_capstyle='butt')
        # energy value title
        ax.text(-0.5, energies[i], "{:.2f}".format(float(e_titles[i])),
                horizontalalignment='center', size='small', color='black',
                verticalalignment='center')
        # state info (J, pi, T, in the form J^p T) title
        plot_title = utils.plot_title_2(channel_titles[i])
        ax.text(10.5, energies[i], plot_title,
                horizontalalignment='center', size='small', color='black',
                verticalalignment='center')
        # width title
        if widths[i] != 0:
            ax.text(x_mid, energies[i], "{:.2f}".format(float(widths[i])),
                    horizontalalignment='center', size='small', color='cyan',
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

    # pick colors for each line
    colours = cmap(np.linspace(0, 1, n_lines))

    # make main figure
    _, axes = plt.subplots(
        nrows=1, ncols=n_spectra, sharex=True, sharey=True,
        figsize=(x_size*n_spectra, y_size), dpi=dpi)
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
            e, w, ct, mt, min_y, max_y, ax=ax, y_label="", colors=colours)

    # set x limits
    plt.xlim(min_x-1, max_x+1)
    # set y limits
    plt.ylim(min_y, max_y)

    # put title only on the first one
    axes[0].set_ylabel("Energy ($MeV$)")

    # then save the plot
    if not os.path.exists("level_schemes"):
        os.mkdir("level_schemes")
    fig_path = os.path.join("level_schemes", "level_scheme")
    plt.savefig(fig_path+".png", dpi=dpi_high_res)
    plt.savefig(fig_path+".svg")
    print("Saved level scheme plot as", fig_path+".png")
