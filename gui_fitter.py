import csv
import numpy as np
from os.path import join
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

from resonance_finder import output_dir

from fitter import read_csv, fit_cubic

# just in case we switch the fit later, I've avoided using the word "cubic"
fit_function = fit_cubic

def make_plot(x, y):
    # basic plot setup
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    # set up sliders
    ax.margins(x=0)
    box_colour = 'lightgoldenrodyellow'
    left_bound_box = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=box_colour)
    right_bound_box = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=box_colour)
    left_slider = Slider(left_bound_box, 'Left', 0.1, 30.0, valinit=min(x))
    right_slider = Slider(right_bound_box, 'Right', 0.1, 10.0, valinit=max(x))

    
    # get best fit function. Note that it's a fit of the form x = fit(y)
    fit = fit_function(y, x)
    fit_y = np.linspace(min(y), max(y), num=1000)
    fit_x = [fit(yi) for yi in fit_y]
    
    # plot data and fit
    data_line, = ax.plot(x, y, 'b-', marker=".", mfc="k")#, lw=0.5)
    fit_line, = ax.plot(fit_x, fit_y, 'g--')
    
    
    def update(val):
        left = left_slider.val
        right = right_slider.val
        
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
        bounded_fit_x = [new_fit(yi) for yi in bounded_fit_y]

        fit_line.set_ydata(bounded_fit_y)
        fit_line.set_xdata(bounded_fit_x)

        ax.set_xlim(min(bounded_x), max(bounded_x))
        ax.set_ylim(min(bounded_y), max(bounded_y)*1.1)

        fig.canvas.draw_idle()


    left_slider.on_changed(update)
    right_slider.on_changed(update)

    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    reset_button = Button(resetax, 'Reset', color=box_colour, hovercolor='0.975')

    def reset(event):
        left_slider.reset()
        right_slider.reset()
    
    reset_button.on_clicked(reset)

    plt.show()



if __name__ == "__main__":
    # get data from csv file
    x, y = read_csv()
    make_plot(x, y)
