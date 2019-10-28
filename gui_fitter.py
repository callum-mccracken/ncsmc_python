"""experimental module for fitting functions to data interactively"""


import csv
import numpy as np
from os.path import join
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox

from utils import output_dir

from fitter import read_csv, fit_cubic, r_squared, best_fit

# just in case we switch the fit later, I've avoided hard-coding "cubic"
fit_function = fit_cubic

def make_plot(x, y, title):
    """this function makes an interactive plot for finding resonances"""
    # I assume x is increasing uniformly, otherwise this whole thing will break
    increment = x[1] - x[0]

    # basic plot setup
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    plt.title("Resonance Finder: "+title)

    # set up sliders
    ax.margins(x=0)
    colour = 'wheat'
    l_bound_box = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=colour)
    h_bound_box = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=colour)
    l_slider = Slider(l_bound_box, 'Low (L/R keys)', min(x), max(x),
                      valinit=min(x))
    h_slider = Slider(h_bound_box, 'High (U/D keys)', min(x), max(x),
                      valinit=max(x))

    # create reset button
    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    reset_button = Button(resetax, 'Reset', color=colour, hovercolor='0.975')

    # get best fit function. Note that it's a fit of the form x = fit(y)
    # since we're going to fit the cubic 
    fit = fit_function(x, y)
    fit_y = np.linspace(min(y), max(y), num=1000)
    fit_x = [fit(yi) for yi in fit_y]
    
    # calculate R^2 value for new fit, stick it in a text box
    r2 = r_squared(x, fit(y))
    # set up on-screen text
    r2_ax = plt.axes([0.7, 0.3, 0.15, 0.05])
    text_box = TextBox(r2_ax, '$R^2 =$', initial="{:5f}".format(r2),
                       color=colour)

    # plot data and fit
    data_line, = ax.plot(x, y, 'b-', marker=".", mfc="k")
    fit_line, = ax.plot(fit_x, fit_y, 'g--')
    #auto_calc_best_fit, ax.plot()

    # function to redraw graph
    def update(val):
        left = l_slider.val
        right = h_slider.val
        
        # get data that is within bounds
        bounded_y = []
        bounded_x = []
        for x_i, y_i in zip(x, y):
            if x_i >= left and x_i <= right:
                bounded_y.append(y_i)
                bounded_x.append(x_i)
        
        data_line.set_ydata(bounded_y)
        data_line.set_xdata(bounded_x)
        
        # make new fit with that data
        new_fit = fit_function(bounded_y, bounded_x)
        bounded_fit_y = np.linspace(min(bounded_y), max(bounded_y), num=1000)
        bounded_fit_x = np.array([new_fit(yi) for yi in bounded_fit_y])

        fit_line.set_ydata(bounded_fit_y)
        fit_line.set_xdata(bounded_fit_x)

        ax.set_xlim(min(bounded_x), max(bounded_x))
        ax.set_ylim(min(bounded_y), max(bounded_y)*1.1)

        # calculate R^2 value for new fit, adjust text box
        r2 = r_squared(bounded_x, np.array([fit(yi) for yi in bounded_y]))
        text_box.set_val("{:5f}".format(r2))


        fig.canvas.draw_idle()
    l_slider.on_changed(update)
    h_slider.on_changed(update)

    # function to reset graph
    def reset(event):
        l_slider.reset()
        h_slider.reset()
    reset_button.on_clicked(reset)

    # function to make bars interactive with keyboard
    def key_event(event):
        # left and right for bottom limit, up and down for top
        if event.key == 'right':
            l_slider.set_val(l_slider.val + increment)
        elif event.key == 'left':
            l_slider.set_val(l_slider.val - increment)
        elif event.key == 'up':
            h_slider.set_val(h_slider.val + increment)
        elif event.key == 'down':
            h_slider.set_val(h_slider.val - increment)

    fig.canvas.mpl_connect('key_press_event', key_event)

    # finally, display the plot
    plt.show()



if __name__ == "__main__":
    # get data from csv file
    resonance_title = "2_-_2_column_2.csv"
    x, y = read_csv(join(output_dir, "CSVs", resonance_title))
    make_plot(x, y, resonance_title)
