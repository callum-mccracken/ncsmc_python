"""things that are useful but didn't really belong anywhere else"""

import os

# make directory where we'll store images of resonances etc
output_dir = os.path.join(os.getcwd(), "resonances")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

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