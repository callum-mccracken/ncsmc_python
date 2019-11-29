"""
Module for fitting cubics to resonances interactively.

Creates GUI with interactive sliders to play with, to set left/right limits.
"""
import csv
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox

# a few global variables to edit as we edit the graphs
width = 0
res_energy = 0


def read_csv(filename):
    """
    Gives the x and y values contained in a 2-column csv file

    filename: string, path to a csv file with 2 columns (for x and y values)

    returns: x, y, arrays of floats
    """
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        csv_values = np.array(list(reader), dtype=float)
    # data_list is structured like [[line, one], [line, two]]
    # we want the transpose, [[col, one], [col, two]]
    csv_values = csv_values.T
    if len(csv_values) != 2:
        raise ValueError("This function can only read two columns!")
    x, y = np.array(csv_values)[:]
    return x, y


def fit_cubic(x, y):
    """
    x, y are 1D arrays of floats.

    Returns cubic, a, b, c, d,
    where cubic is the callable best-fit function y = cubic(x),
    and a, b, c, d are the coefficients (floats)
    """
    d, c, b, a = np.polyfit(x, y, 3)

    def cubic(x):
        return a + b * x + c * x ** 2 + d * x ** 3
    return cubic, a, b, c, d


def make_plot(x, y, title):
    """
    This function makes an interactive plot for finding resonances.

    x, y = 1D arrays of floats, title = string

    Requires the ability to open a window and interact with it.

    returns [(width of resonance), (energy of resonance)]

    (both list elements are floats)
    """
    global res_energy, width

    # there are a bunch of style parameters here that I had to play with
    # manually. If you can think of a better way to set up the graph,
    # please do so, but currently if you want to change anything it might get
    # messy, just so you know.

    clear = (0, 0, 0, 0)  # RGBA clear
    triumf_blue = "#009fdf"  # hex code for a blue color

    n_fit = 100  # how many points to draw when we plot the cubic fit line

    increment = x[1] - x[0]  # x should be increasing uniformly

    # basic plot setup
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    plt.title("Resonance Finder\n"+title)
    plt.xlabel("Energy ($MeV$)")
    plt.ylabel("Phase ($^\\circ$)")
    ax.margins(x=0)

    # set up left/right limit sliders
    r_bound_box = plt.axes((0.25, 0.1, 0.65, 0.03), facecolor=clear)
    l_bound_box = plt.axes((0.25, 0.06, 0.65, 0.03), facecolor=clear)
    r_slider = Slider(r_bound_box, 'Right (U/D keys)', min(x), max(x),
                      valinit=max(x), color=triumf_blue)
    l_slider = Slider(l_bound_box, 'Left (L/R keys)', min(x), max(x),
                      valinit=min(x), color=triumf_blue)

    # reset button
    reset_ax = plt.axes((0.7, 0.01, 0.1, 0.04))
    reset_button = Button(reset_ax, 'Reset',
                          color=clear, hovercolor=triumf_blue)

    # done button
    done_ax = plt.axes((0.8, 0.01, 0.1, 0.04))
    done_button = Button(done_ax, 'Done', color=clear, hovercolor=triumf_blue)

    # fit the cubic y = cubic(x)
    cubic, _, b, c, d = fit_cubic(x, y)
    fit_x = np.linspace(min(x), max(x), num=n_fit)
    fit_y = [cubic(xi) for xi in fit_x]

    # calculate resonance energy, resonance width
    res_energy = - c / (3 * d)
    width = 2 / np.radians(b + 2*c*res_energy + 3*d*res_energy**2)

    # set up on-screen text
    res_energy_ax = plt.axes((0.7, 0.3, 0.2, 0.05))
    res_energy_text_box = TextBox(
        res_energy_ax, '$E_{resonance} =$',
        initial="{:2f}".format(res_energy), color=clear)
    width_ax = plt.axes((0.7, 0.35, 0.2, 0.05))
    width_text_box = TextBox(
        width_ax, '$Width =$',
        initial="{:2f}".format(width), color=clear)
    points_ax = plt.axes((0.7, 0.25, 0.2, 0.05))
    points_text_box = TextBox(
        points_ax, '$N_{points} =$',
        initial=str(len(x)), color=clear)

    # plot data and fit
    data_line, = ax.plot(x, y, '-', color=triumf_blue)
    fit_line, = ax.plot(fit_x, fit_y, 'k--')

    # function to redraw graph
    def update(val):
        global res_energy, width
        left = l_slider.val
        right = r_slider.val

        # get data that is within bounds
        indices = (left <= x) * (x <= right)
        bounded_x = x[indices]
        bounded_y = y[indices]

        data_line.set_ydata(bounded_y)
        data_line.set_xdata(bounded_x)

        # make new fit with that data
        cubic, _, b, c, d = fit_cubic(bounded_x, bounded_y)
        bounded_fit_x = np.linspace(min(bounded_x), max(bounded_x), num=n_fit)
        bounded_fit_y = np.array([cubic(xi) for xi in bounded_fit_x])

        fit_line.set_ydata(bounded_fit_y)
        fit_line.set_xdata(bounded_fit_x)

        ax.set_xlim(min(bounded_x), max(bounded_x))
        ax.set_ylim(min(bounded_y), max(bounded_y)*1.1)

        # calculate values for text boxes
        res_energy = - c / (3 * d)
        res_energy_text_box.set_val("{:2f}".format(res_energy))

        width = 2 / np.radians(
            b + 2*c*res_energy + 3*d*res_energy**2)
        width_text_box.set_val("{:2f}".format(width))

        points_text_box.set_val(str(len(bounded_x)))

        fig.canvas.draw_idle()

    l_slider.on_changed(update)
    r_slider.on_changed(update)

    # function to reset graph
    def reset(event):
        l_slider.reset()
        r_slider.reset()
    reset_button.on_clicked(reset)

    # function to exit graph when done
    def close_plot(event):
        plt.close()
        plt.cla()
        plt.clf()
    done_button.on_clicked(close_plot)

    # function to make bars interactive with keyboard
    def key_event(event):
        # left and right for bottom limit, up and down for top
        if event.key == 'right':
            l_slider.set_val(l_slider.val + increment)
        elif event.key == 'left':
            l_slider.set_val(l_slider.val - increment)
        elif event.key == 'up':
            r_slider.set_val(r_slider.val + increment)
        elif event.key == 'down':
            r_slider.set_val(r_slider.val - increment)

    fig.canvas.mpl_connect('key_press_event', key_event)

    # finally, display the plot
    plt.show()
    plt.close()
    plt.cla()
    plt.clf()

    # TODO: for some reason, you still have to hit the x in the corner to close
    # the graph... Why?

    # return useful info once the plot is closed
    return [width, res_energy]


def find_resonance(csv_filename):
    """
    Finds the energy at which a resonance occurs for given channel.

    Requires a csv file with a name of the form

    ``path/to/file/phase_1_-_3_column_4_Nmax_4.csv``

    or more generally,

    ``path/to/file/[word]_[2J]_[parity]_[2T]_column_[col]_Nmax_[Nmax].csv``
    """
    # get the important stuff out of filename
    filename = os.path.split(csv_filename)[-1]
    filename = filename.replace(".csv", "")
    # "important stuff" = [word]_[2J]_[parity]_[2T]_column_[col]_Nmax_[Nmax]
    _, J2, parity, T2, _, _, _, _ = filename.split("_")

    # are J and T integers?
    J_int = int(J2) / 2 == int(int(J2) / 2)
    T_int = int(T2) / 2 == int(int(T2) / 2)

    # strings for J and T, either in fraction or integer form
    J = str(int(int(J2) / 2)) if J_int else "\\frac{{{}}}{{{}}}".format(J2, 2)
    T = str(int(int(T2) / 2)) if T_int else "\\frac{{{}}}{{{}}}".format(T2, 2)

    # get data from csv file
    x, y = read_csv(csv_filename)

    nice_title = "$J={},\\pi={},T={}$".format(J, parity, T)

    # res_info = [resonance width, resonance energy]
    res_info = make_plot(x, y, nice_title)
    return res_info


def save_info(csv_path, titles, widths, energies):
    """
    Save titles, widths, and energies to a csv file.

    titles = list of srings

    energies, widths = lists of floats

    csv_path = string
    """
    file_string = "2J_parity_2T_column,width,energy\n"
    energies = [str(e) for e in energies]
    widths = [str(w) for w in widths]
    for title, width, energy in zip(titles, widths, energies):
        file_string += ",".join([title, width, energy]) + "\n"
    with open(csv_path, "w+") as csv_file:
        csv_file.write(file_string)
