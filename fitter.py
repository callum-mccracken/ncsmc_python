import csv
import numpy as np
from os.path import join
import matplotlib.pyplot as plt

from utils import output_dir

def read_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        data = np.array(list(reader), dtype=float)
    # data_list is structured like [[line, one], [line, two]]
    # we want the transpose, [[col, one], [col, two]]
    data = data.T
    if len(data) != 2:
        raise ValueError("This function was only made for reading two columns!")
    x, y = data[:]
    return x, y

def monotonic_sections(x,y):
    sections = []
    monotonic_x = []
    monotonic_y = []
    for x_i, y_i in zip(x, y):
        if len(monotonic_y) < 2:  # append the first two entries for sure
            monotonic_x.append(x_i)
            monotonic_y.append(y_i)
        else:
            # check to see if the next data point is still monotonic
            increasing = monotonic_y[1] > monotonic_y[0]
            if increasing and (y_i >= monotonic_y[-1]):
                monotonic_x.append(x_i)
                monotonic_y.append(y_i)
            elif (not increasing) and (y_i <= monotonic_y[-1]):
                monotonic_x.append(x_i)
                monotonic_y.append(y_i)
            else:  # if not monotonic, restart the lists
                sections.append([monotonic_x, monotonic_y])
                monotonic_x = [x_i]
                monotonic_y = [y_i]
    # ensure we still append the last section
    sections.append([monotonic_x, monotonic_y])
    return np.array(sections)

def useful_sections(monotonic_sections):
    sections = []
    for section in monotonic_sections:
        x, y = section
        # we'll ignore sections with less than 10 points
        if len(x) < 10:
            continue
        # ignore sections that are constant, they won't have resonances
        if all([y_i == y[0] for y_i in y]):
            continue
        # ignore decreasing sections
        if any([y_i < y[0] for y_i in y]):
            continue
        # if all these checks pass, append the section
        sections.append(section)
    return np.array(sections)        

def flip_x_y(sections):
    for i, section in enumerate(sections):
        x, y = section
        sections[i] = [y, x]
    return np.array(sections)

def fit_cubic(x, y):
    z = np.polyfit(x, y, 3)
    a, b, c, d = reversed(z)
    def cubic(x):
        return a + b * x + c * x**2 + d * x**3
    return cubic

def plot_fit(x, y, fit_func):
    fit_x = np.linspace(min(x), max(x), num=1000)
    fit = [fit_func(x_i) for x_i in fit_x]
    plt.plot(y, x)
    plt.plot(fit, fit_x)
    plt.show()

def r_squared(y, y_fit):
    mean = np.mean(y)
    # ss = sum of squares
    ss_real = np.sum((y - mean) ** 2)
    ss_fit = np.sum((y_fit - mean) ** 2)
    # r-squared is defined as this
    r2 = 1 - (ss_fit / ss_real)
    return r2

def best_fit(x, y):
    # separate into monotonic sections
    sections = monotonic_sections(x, y)
    # only worry about the possibly useful sections
    sections = useful_sections(sections)
    # flip x and y in each section
    sections = flip_x_y(sections)
    
    # get r_squared values and energies for each section
    r_squared_values = []
    fit_funcs = []
    for section in sections:
        sec_x, sec_y = section
        # cubic is a function
        cubic = fit_cubic(sec_x, sec_y)
        fit_funcs.append(cubic)
        # get value where 
        y_fit = np.array([cubic(x_i) for x_i in sec_x])
        r_squared_values.append(r_squared(sec_y, y_fit))

    # is it safe to assume all R^2 values are unique?
    if len(r_squared_values) != len(set(r_squared_values)):
        raise ValueError("There are some non-unique R^2 values")
    
    max_r2 = max(r_squared_values)
    max_r2_index = r_squared_values.index(max_r2)

    best_fit_func = fit_funcs[max_r2_index]
    
    return best_fit_func

if __name__ == "__main__":
    # get data from csv file
    x, y = read_csv(join(output_dir, "CSVs", "0_-_0_column_2.csv"))
    best_fit(x, y)