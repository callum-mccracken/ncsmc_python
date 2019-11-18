# libraries and data
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# general plot formatting
plt.style.use('seaborn-white')

# we'll pick colours from this colormap
cmap = plt.get_cmap('viridis')

dpi=96
# dimensions of spectrum plots
x_size = 5
y_size = 10


def plot_levels(energies, widths, channel_titles, main_title,
                ax=None, y_label="Energy ($MeV$)", colors=None):
    """makes a plot of a single level scheme"""
    # set up plot
    if ax == None:
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

    # x values, it won't change much if you adjust this, but just be sure
    # it has a non-zero length, or the lines on the plot will be dots
    x = range(1, 11)
    # Change xlim
    ax.set_xlim(0,len(x)+2)

    # format energies for plotting
    e_titles = ["{}".format(e) for e in energies]
    e_list = [[e]*len(x) for e in energies]

    # plot each energy line
    for i, e in enumerate(e_list):
        ax.plot(x, e, marker='', color=colors[i],
                 linewidth=widths[i], alpha=0.7)

    # annotate each line
    for i, main_title in enumerate(e_titles):
        ax.text(len(x)*1.05, i*0.99, main_title,
                 horizontalalignment='left', size='small', color='black')

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

    # plot each individual spectrum
    for ax, e, w, ct, mt in zip(axes, energies_list, widths_list,
                                channel_title_list, main_title_list):
        plot_levels(e, w, ct, mt, ax=ax, y_label="", colors=colours)

    # put title only on the first one
    axes[0].set_ylabel("Energy ($MeV$)")
    # then show the plot
    plt.show()

if False:
    # you provide the csv and titles
    files = ["resonance_info_Nmax_4"]



    n_spectra = 3

    # list of energies to plot
    e_vals = list(range(10))

    # widths of resonances, 1 to 10, where 10 is the largest width and 1 is bound
    widths = [i+1 for i in range(10)]

    e_list = [e_vals for _ in range(n_spectra)]
    width_list = [widths for _ in range(n_spectra)]
    title_list = ["$2\\hbar\\omega$", "$4\\hbar\\omega$", "$6\\hbar\\omega$"]

    if len(title_list) != n_spectra:
        raise ValueError("incorrect number of titles, n_spectra = "+str(n_spectra))
    if len(e_list) != n_spectra:
        raise ValueError("incorrect numbe, n_spectra = "+str(n_spectra))


    plot_multi_levels(e_list, width_list, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], title_list)