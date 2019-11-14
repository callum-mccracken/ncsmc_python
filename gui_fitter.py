"""module for fitting functions to data interactively"""
import csv
import numpy as np
from os.path import join
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox

from utils import output_dir


def read_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        csv_values = np.array(list(reader), dtype=float)
    # data_list is structured like [[line, one], [line, two]]
    # we want the transpose, [[col, one], [col, two]]
    csv_values = csv_values.T
    if len(csv_values) != 2:
        raise ValueError("This function was only made for reading two columns!")
    x, y = csv_values[:]
    return x, y


def fit_cubic(x, y):
    """a fit of the form a + bx + cx^2 + dx^3"""
    d, c, b, a = np.polyfit(x, y, 3)
    def cubic(x):
        return a + b * x + c * x ** 2 + d * x ** 3
    return cubic, a, b, c, d


def make_plot(x, y, title):
    """this function makes an interactive plot for finding resonances"""

    n_fit = 100  # how many points to draw when we plot the fit

    increment = x[1] - x[0]  # x is increasing uniformly, right???

    # basic plot setup
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    plt.title("Resonance Finder\n"+title)
    plt.xlabel("Energy ($MeV$)")
    plt.ylabel("Phase ($^\\circ$)")
    ax.margins(x=0)

    # set up sliders
    clear = (0, 0, 0, 0)  # RGBA clear
    triumf_blue = "#009fdf"
    r_bound_box = plt.axes((0.25, 0.1, 0.65, 0.03), facecolor=clear)
    l_bound_box = plt.axes((0.25, 0.06, 0.65, 0.03), facecolor=clear)
    r_slider = Slider(r_bound_box, 'Right (U/D keys)', min(x), max(x),
                      valinit=max(x), color=triumf_blue)
    l_slider = Slider(l_bound_box, 'Left (L/R keys)', min(x), max(x),
                      valinit=min(x), color=triumf_blue)

    # create reset button
    resetax = plt.axes((0.8, 0.01, 0.1, 0.04))
    reset_button = Button(resetax, 'Reset', color=clear, hovercolor='0.975')

    # fit the cubic y = cubic(x)
    cubic, _, b, c, d = fit_cubic(x, y)
    fit_x = np.linspace(min(x), max(x), num=n_fit)
    fit_y = [cubic(xi) for xi in fit_x]

    # calculate resonance E, width
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
        left = l_slider.val
        right = r_slider.val
        
        # get data that is within bounds
        indices = (left <= x) * (x <= right)
        bounded_x = x[indices]
        bounded_y = y[indices]
        
        data_line.set_ydata(bounded_y)
        data_line.set_xdata(bounded_x)
        
        # make new fit with that data
        new_cubic, _, new_b, new_c, new_d = fit_cubic(bounded_x, bounded_y)
        bounded_fit_x = np.linspace(min(bounded_x), max(bounded_x), num=n_fit)
        bounded_fit_y = np.array([new_cubic(xi) for xi in bounded_fit_x])

        fit_line.set_ydata(bounded_fit_y)
        fit_line.set_xdata(bounded_fit_x)

        ax.set_xlim(min(bounded_x), max(bounded_x))
        ax.set_ylim(min(bounded_y), max(bounded_y)*1.1)

        # calculate values for text boxes
        new_e_res = - new_c / (3 * new_d)
        res_energy_text_box.set_val("{:2f}".format(new_e_res))

        new_width = 2 / np.radians(
            new_b + 2*new_c*new_e_res + 3*new_d*new_e_res**2)
        width_text_box.set_val("{:2f}".format(new_width))

        points_text_box.set_val(str(len(bounded_x)))

        fig.canvas.draw_idle()

    l_slider.on_changed(update)
    r_slider.on_changed(update)

    # function to reset graph
    def reset(event):
        l_slider.reset()
        r_slider.reset()
    reset_button.on_clicked(reset)

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

def find_resonance(csv_filename):
    # get data from csv file
    x, y = read_csv(join(output_dir, "CSVs", csv_filename))
    
    J2, parity, T2, _, _ = csv_filename[:-4].split("_")
    J_int = int(J2) / 2 == int(int(J2) / 2)
    T_int = int(T2) / 2 == int(int(T2) / 2)
    

    J = str(int(int(J2) / 2)) if J_int else "$\\frac{"+J2+"}{2}$"
    T = str(int(int(T2) / 2)) if T_int else "$\\frac{"+T2+"}{2}$"

    nice_title = "$J$: " + J + ", $\\pi$: " + parity + ", $T$: " + T

    make_plot(x, y, nice_title)




if __name__ == "__main__":
    find_resonance("2_-_2_column_2.csv")
