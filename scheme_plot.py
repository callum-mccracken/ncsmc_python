import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import utils

# general plot formatting
plt.style.use('seaborn-white')

# we'll pick colours from this colormap
cmap = plt.get_cmap('viridis')

dpi=96
# dimensions of spectrum plots
x_size = 5
y_size = 10

def linewidth_from_data_units(linewidth, axis, reference='y'):
    """
    Convert a linewidth in data units to linewidth in points.

    """
    #Thanks! https://stackoverflow.com/questions/19394505/matplotlib-expand-the-line-with-specified-width-in-data-unit
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
                ax=None, y_label="Energy ($MeV$)", colors=None):
    """makes a plot of a single level scheme"""
    # set up plot
    if ax is None:
        _, ax = plt.subplots(figsize=(x_size, y_size), dpi=dpi)

    # get colors for spectra if they're not given
    if colors is None:
        colors = cmap(np.linspace(0, 1, len(energies)))

    # Add titles
    ax.set_title("{}".format(main_title), loc='center',
              fontsize=12, fontweight=2, color='black')
    ax.set_xlabel("")
    ax.set_ylabel(y_label)
    ax.set_xticks([])

    # x values, one for each resonance
    x = range(len(energies)+1)
    # Change xlim
    ax.set_xlim(min(x)-1, max(x)+1)

    # format energies for plotting
    e_titles = ["{}".format(e) for e in energies]
    e_list = [[e]*len(x) for e in energies]

    # make an initial skinny plot for each energy value
    for i, e in enumerate(e_list):
        ax.plot(x, e, marker='', color='k', linewidth=1, alpha=1,
                solid_capstyle="butt")

    # set limits for which widths we'll consider out of bounds
    factor = 0.2
    max_y = max(energies) + factor * (max(energies)-min(energies))
    min_y = min(energies) - factor * (max(energies)-min(energies))


    # plot each energy line with a bar around it depending on width
    for i, e in enumerate(e_list):
        # figure out if this energy's width will fit on the plot
        top = energies[i] + widths[i]
        btm = energies[i] - widths[i]
        itll_fit = top < max_y and btm > min_y

        if widths[i] == 0:  # bound state
            ax.plot(x, e, marker='', color="green",
                    linewidth=1, alpha=1, solid_capstyle="butt")
        elif itll_fit:  # typical resonance where the width bars will fit
            x_width = linewidth_from_data_units(1, ax, reference="x")
            x_mid = (x[i] + x[i+1]) / 2
            ax.plot([x_mid, x_mid], [top, btm], marker='', color=colors[i],
                    linewidth=x_width, alpha=0.7, solid_capstyle='butt')
            ax.plot(x[i:i+2], e[i:i+2], "--", marker='', color='cyan',
                    linewidth=1, alpha=1, solid_capstyle='butt')
        else:  # if width is too huge to put on the plot, make it a red line
            ax.plot(x, e, marker='', color="red",
                    linewidth=5, alpha=0.5, solid_capstyle='butt')

    # annotate each line with energy value
    for i, e_title in enumerate(e_titles):
        ax.text(-0.5, energies[i], "{:.2f}".format(float(e_title)),
                 horizontalalignment='center', size='small', color='black',
                 verticalalignment='center')
    # annotate each line with state info (J, pi, T, in the form J^p T)
    for i, c_title in enumerate(channel_titles):
        plot_title = utils.plot_title_2(c_title)
        ax.text(len(x)-0.5, energies[i], plot_title,
                 horizontalalignment='center', size='small', color='black',
                 verticalalignment='center')


def plot_multi_levels(energies_list, widths_list, channel_title_list,
                      main_title_list):
    """make plots of many different spectra on one figure"""
    n_spectra = len(energies_list)
    n_lines = max([len(e) for e in energies_list])

    # pick colors for each line
    colours = cmap(np.linspace(0, 1, n_lines))

    # make main figures
    _, axes = plt.subplots(
        nrows=1, ncols=n_spectra, sharex=True, sharey=True,
        figsize=(x_size*n_spectra, y_size), dpi=dpi)
    if type(axes) != np.ndarray:
        axes = [axes]

    # plot each individual spectrum
    for ax, e, w, ct, mt in zip(axes, energies_list, widths_list,
                                channel_title_list, main_title_list):
        plot_levels(e, w, ct, mt, ax=ax, y_label="", colors=colours)

    # put title only on the first one
    axes[0].set_ylabel("Energy ($MeV$)")
    # then show the plot
    plt.show()

