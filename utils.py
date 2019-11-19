"""things that are useful but didn't really belong anywhere else"""

import os

# directory where we'll store info about resonances
output_dir = os.path.join(os.path.dirname(__file__), "resonances_Nmax_{}")

def abs_path(path):
    """return the absolute path to a file"""
    # first expand ~ for the user
    path = os.path.expanduser(path)
    # then get rid of any ../ or ./ items
    path = os.path.realpath(path)
    # TODO: anything else we should do? Like deal with environment variables?
    return path

def is_float(string):
    """checks if a string can be cast as a float"""
    try:
        _ = float(string)
        return True
    except ValueError:
        return False

def index_list(input_list):
    """returns indices for smallest to largest values in input_list,
    no repeat values allowed.
    
    Same idea as list.index() but that gives repeats"""
    
    sorted_index_list = []
    s_input_list = sorted(input_list)
    used = [False for element in input_list]
    for element in s_input_list:
        index = input_list.index(element)
        # if we've already counted this one, take the next
        while used[index]:
            new_list = input_list[index+1:]
            index = len(input_list)-len(new_list) + new_list.index(element)
        sorted_index_list.append(index)
        used[index] = True

    # double-check we don't have any repeats
    assert all([i in sorted_index_list for i in range(len(input_list))])

    return sorted_index_list

def multi_strip(string, list_of_strs):
    """
    Returns the string but stripped of substrings
    
    Same idea as string.strip(), but for many arguments
    """
    for s in list_of_strs:
        if s == "":  # ignore this case
            continue
        while s in string:
            string = string.replace(s, "")
    return string

def make_nice_title(xmtitle):
    """makes nicer-looking titles than the ones provided in xmgrace files"""
    # we'll want a good title for plotting etc., so remove all gross bits
    nice_title = multi_strip(xmtitle, ["\n", "\\", "S", "N", "@", "legend"])
    # remove s0, s1, ..., (the first word), that's just used for xmgrace
    nice_title = nice_title[nice_title.index('"'):]
    # remove quotes and replace spaces with underscores
    nice_title = nice_title.replace('"', "").replace(" ", "_")
    # put underscores between 2J, parity, 2T
    if "+" in nice_title:
        parity_index = nice_title.index("+")
        parity = "+"
    elif "-" in nice_title:
        parity_index = nice_title.index("-")
        parity = "-"
    else:
        raise ValueError("No +- parity specified... Title is "+xmtitle)
    j2 = nice_title[:parity_index]
    t2 = nice_title[parity_index+1:]
    nice_title = "_".join([j2, parity, t2])
    return nice_title


def make_plot_title(nice_title):
    """makes a plottable, LaTeX formatted title, for use in matplotlib graphs"""
    hunks = nice_title.split("_")
    print(hunks)
    if len(hunks) == 5:
        J2, parity, T2, _, col = hunks
    elif len(hunks) == 4:
        J2, parity, T2, col = hunks
    else:
        raise ValueError("Too many or too few hunks!")
    J = float(J2) / 2
    if J == int(J):
        J = str(J)
    else:
        J = "\\frac{{{}}}{{{}}}".format(J2, 2)
    T = float(T2) / 2
    if T == int(T):
        T = str(T)
    else:
        T = "\\frac{{{}}}{{{}}}".format(T2, 2)
    plot_title = "$J={}, \\pi={}, T={}$, column {}".format(
        J, parity, T, col)
    return plot_title



def xmgrace_title(xmtitle, series_num):
    """Takes an xmgrace series title and edits the series number,
    setting it equal to series_num."""

    # xmtitle has the general format "@ s[num] [...]"
    # and we want it to end up looking like "@ s[series_num] [...]"

    # break up into "words", separated by spaces
    words = xmtitle.split()

    # the 1th word should be "s[num]". Set it to "s[series_num]" instead.
    words[1] = "s" + str(series_num)

    # rejoin the words
    new_title = " ".join(words)

    # ta-da!
    return new_title