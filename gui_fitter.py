"""module for fitting functions to data interactively"""
import numpy as np
from os.path import join
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox

from utils import output_dir

from fitter import read_csv, fit_cubic

n_fit = 100  # how many points to draw for the fit

def make_plot(x, y, title):
    """this function makes an interactive plot for finding resonances"""
    # x is increasing uniformly, right???
    increment = x[1] - x[0]

    # basic plot setup
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    plt.title("Resonance Finder\n"+title)
    plt.xlabel("Energy ($MeV$)")
    plt.ylabel("Phase ($\\circ$)")

    # set up sliders
    ax.margins(x=0)
    colour = 'wheat'
    r_bound_box = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=colour)
    l_bound_box = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=colour)
    r_slider = Slider(r_bound_box, 'Right (U/D keys)', min(x), max(x),
                      valinit=max(x))
    l_slider = Slider(l_bound_box, 'Left (L/R keys)', min(x), max(x),
                      valinit=min(x))
    
    # create reset button
    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    reset_button = Button(resetax, 'Reset', color=colour, hovercolor='0.975')

    # get best fit function. Note that it's a fit of the form x = fit(y)
    # since we're going to fit the cubic 
    cubic, _, b, c, d = fit_cubic(x, y)
    fit_y = np.linspace(min(y), max(y), num=n_fit)
    fit_x = cubic(fit_y)
    
    # calculate steepest point, 2/derivative (in  radians) there
    steepest_x = - c / (3 * d)
    two_over_dydx = 2 / np.radians(b + 2*c*steepest_x + 3*d*steepest_x**2)

    # set up on-screen text
    steep_ax = plt.axes([0.7, 0.3, 0.15, 0.05])
    steep_text_box = TextBox(steep_ax, '$E_{steep} =$',
                             initial="{:5f}".format(steepest_x), color=colour)
    two_over_dydx_ax = plt.axes([0.3, 0.3, 0.15, 0.05])
    dydx_text_box = TextBox(two_over_dydx_ax, '$dydx =$',
                       initial="{:5f}".format(two_over_dydx), color=colour)

    # plot data and fit
    data_line, = ax.plot(x, y, 'b-', marker=".", mfc="k")
    fit_line, = ax.plot(fit_x, fit_y, 'g--')

    # function to redraw graph
    def update(val):
        left = l_slider.val
        right = r_slider.val
        
        # get data that is within bounds
        indices = np.where((left <= x) <= right)
        bounded_y = y[indices]
        bounded_x = x[indices]
        
        data_line.set_ydata(bounded_y)
        data_line.set_xdata(bounded_x)
        
        # make new fit with that data
        new_cubic, _, b, c, d = fit_cubic(bounded_y, bounded_x)
        bounded_fit_y = np.linspace(min(bounded_y), max(bounded_y), num=n_fit)
        bounded_fit_x = new_cubic(bounded_fit_y)

        fit_line.set_ydata(bounded_fit_y)
        fit_line.set_xdata(bounded_fit_x)

        ax.set_xlim(min(bounded_x), max(bounded_x))
        ax.set_ylim(min(bounded_y), max(bounded_y)*1.1)

        # calculate values for text boxes
        steepest_x = - c / (3 * d)
        two_over_dydx = 2 / np.radians(b + 2*c*steepest_x + 3*d*steepest_x**2)
        steep_text_box.set_val("{:5f}".format(steepest_x))
        dydx_text_box.set_val("{:5f}".format(two_over_dydx))
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



if __name__ == "__main__":
    # get data from csv file
    resonance_title = "2_-_2_column_2.csv"
    x, y = read_csv(join(output_dir, "CSVs", resonance_title))
    
    J2, parity, T2, _, col = resonance_title[:-4].split("_")
    J_int = int(J2) / 2 == int(int(J2) / 2)
    T_int = int(T2) / 2 == int(int(T2) / 2)
    

    J = str(int(J2) / 2) if J_int else "$\\frac{"+J2+"}{2}$"
    T = str(int(T2) / 2) if T_int else "$\\frac{"+T2+"}{2}$"

    nice_title = "$J$: " + J + ", $\\pi$: " + parity + ", $T$: " + T

    make_plot(x, y, nice_title)
