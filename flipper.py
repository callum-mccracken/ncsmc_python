"""
Contains a whole bunch of functions which...

- read ncsmc output files

- clean them up for processing

- remove unphysical jumps in the data caused by "wrapping"
  (e.g. -89.8, -89.9, 89.9)

- reorder columns so that they are consistent as one scrolls down

- allow you to pick out individual channels

"""
import argparse

import numpy as np

import utils

filepath = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/to_be_flipped/big_eigenphase_shift.agr"

def flip_if_needed(last_nums, nums):
    """Compare every number in nums to every one in last_nums.
    If the difference is big, flip the number in nums until we make it small.

    By "flip", I mean add or subtract 180, as needed.

    Return the new list of nums, after being flipped if needed
    """
    for i in range(len(last_nums)):  # there might be more new nums than old
        num = nums[i]
        last_num = last_nums[i]
    
        if abs(last_num - num) >= 50:
            num = num + np.sign(last_num - num) * 180
        nums[i] = num
    return nums


def sanitize(filename):
    """
    Opens NCSMC output file, reads each line, separates into text lines and
    number lines. Sets NaN values to zero.
    
    Returns lists:
    - one for title lines, contains strings
    - one for number lines, each entry is a sub-list of floats
    """
    with open(filename, "r+") as read_file:
        lines = read_file.readlines()
    text_lines = []
    number_lines = []
    for line in lines:
        nums = line.split()
        # replace all NaNs with zero
        for i, num in enumerate(nums):
            if num == "NaN":
                nums[i] = 0
        if not all(utils.is_float(num) for num in nums):
            # save these for title purposes
            text_lines.append(line)
        else:
            # save numbers for analysis later
            nums = [float(n) for n in nums]
            number_lines.append(nums)
    return text_lines, number_lines


def separate_into_sections(list_of_nums):
    """returns sections of the file based on line length"""
    # list_of_nums is a list of lists of numbers, 
    # from the file but not strings anymore
    sections = []
    section = []
    last_length = 0  # since we can't assume every file starts with 2 cols
    for line in list_of_nums + [[0]]:
        # the list at the end ensures that we save the last section
        if len(line) == last_length:
            section.append(line)
        else:
            if section != []:  # no sense keeping sections with no lines
                sections.append(section)
            section = [line]
            last_length = len(line)

    # check that section creation worked:
    for section in sections:
        top = section[0]
        bottom = section[-1]
        if not (len(top) == len(bottom)):
            raise ValueError("Why does section have lines of different length?")

    return sections


def separate_into_megasections(sections):
    """maybe calling them megasections was a little dramatic,
    but megasections are the sections of the input file separated by titles,
    rather than sections, which are separated by changing line length
    """

    # make mega_sections (combine sections of increasing size)
    mega_sections = []
    while len(sections) > 1: 
        top_section = sections[-2]
        bottom_section = sections[-1]
        # lines at the interface
        top_line = top_section[-1]
        bottom_line = bottom_section[0]
        if len(top_line) > len(bottom_line):
            mega_sections.append(bottom_section)
            sections.pop()
        else:
            sections[-2] = top_section + bottom_section
            sections.pop()
    
    if len(sections) == 1:
        mega_sections.append(sections[0])
    else:
        raise ValueError("How did this happen?")
    
    return list(reversed(mega_sections))  # now it's top-to-bottom


def separate_into_channels(filename):
    """returns channels (as lists of floats) with associated labels (strings)
    
    Also returns energies associated with each row. Note that not all
    channels have the same length as the energy list
    """
    text_lines, num_lines = sanitize(filename)
    sections = separate_into_sections(num_lines)

    titles = []
    for line in text_lines:
        if "&" not in line:  # all that's left is titles
            titles.append(line)

    mega_sections = separate_into_megasections(sections)

    # initialize channels dict
    channels = {}
    for ms, ms_title in zip(mega_sections, titles):
        # largest number of columns in the mega_section
        max_cols = max(len(line) for line in ms)

        # note that we're ignoring energy columns here (the first columns)
        
        channel_title_fmt = ms_title+" column {}"
        channel_titles = [
            channel_title_fmt.format(i) for i in range(1, max_cols)]  
        
        for i in range(max_cols-1):
            channels[channel_titles[i]] = []

        # get data for each channel        
        for line in ms:
            for i, num in enumerate(line[1:]):
                channels[channel_titles[i]].append(num)

    # now make list to contain energy values
    energies = [line[0] for line in mega_sections[0]]
    
    return channels, energies


def do_one_flip(section):
    """perform the flip operation on one section one time"""
    new_section = section
    compare_line = section[0]  # we'll always compare to the line before
    for i, line in enumerate(section):
        if i == 0:  # never adjust the first line
            continue
        # now just check for +- swaps that need to happen
        new_section[i] = flip_if_needed(compare_line, line)
        compare_line = new_section[i]
    return new_section


def flip_one_section(section):
    """perform flip operation on a section until fully finished"""
    # sections have the same number of columns all the way through
    new_section = []
    while new_section != section:
        new_section = do_one_flip(section)
    return new_section


def write_data(sections, text_lines, filename):
    """write flipped data back into a file,
    making sure to put the text lines (i.e. titles) back in the right spots"""
    write_filename = filename+'_flipped'
    text_line_counter = 0
    tlc = text_line_counter
    with open(write_filename, "w+") as write_file:        
        # start with a title
        write_file.write(text_lines[tlc])
        tlc += 1
        for i, section in enumerate(sections):
            for line in section:
                line_str = ""
                for num in line:
                    line_str += "{:10.5f} ".format(num)
                line_str += "\n"
                write_file.write(line_str)
            # write title in the middle if needed
            if i != len(sections) - 1:
                top_section = sections[i]
                bottom_section = sections[i+1]    
                # lines at the interface
                top_line = top_section[-1]
                bottom_line = bottom_section[0]
                if len(top_line) > len(bottom_line):
                    # next title and "&"
                    write_file.write(text_lines[tlc])
                    tlc += 1
                    write_file.write(text_lines[tlc])
                    tlc += 1
        # end with a "&"
        write_file.write(text_lines[tlc])
        tlc += 1
    return write_filename


def dist(a, b):
    """compares a and b "up to flips", i.e. mod 180"""
    a_mod = a % 180
    b_mod = b % 180
    d = abs(a_mod - b_mod)
    return d


def get_column_map(top_line, bottom_line):
    """
    get a dict of the form 
    
    map ={
        0: index0,
        1: index1,
        ...
    }
    
    so if you're wondering what column in the top line corresponds
    to which one in the bottom line, you can use this mapping.

    To apply a column mapping easily, use apply_col_mapping()

    but the ideas is that you just say you just say
    
    b = [b[map[i]] for i in range(len(b))]
    
    and then b has the same column order as a.
    """
    # abbreviate so they're easier to type
    a = top_line
    b = bottom_line

    # ensure lines have same length, so really we're making a mapping from
    # top_line to a chunk of bottom line
    assert len(a) == len(b)

    # this will be the mapping from "b ordering" to "a ordering"
    mapping = {n: n for n in range(len(b))}
    used_in_mapping = [False for _ in range(len(b))]
    used_in_mapping[0] = True  # ignore zeroth column -- energies

    for i, a_i in enumerate(a):
        # skip 0th column (energies are fixed in place)
        if i == 0:
            continue
        # say distance to zeroth column is huge so we never pick energies
        distances = [1000000] + [dist(a_i, b_j) for b_j in b[1:]]
        # indices will be sorted smallest to largest
        # and must contain all numbers up to len(a)
        # I wanted to just use distanced.index(x) for x in sorted(distances)
        # but that only gives the first index
        indices = utils.index_list(distances[:len(a)])
        # now take the index with the minimum distance that has not been used
        min_index = 0
        while used_in_mapping[indices[min_index]]:
            min_index += 1
        mapping[i] = indices[min_index]
        used_in_mapping[indices[min_index]] = True

    # check map is valid (if it's not injective we're going to have a bad time)
    outputs = []
    for output in mapping.values():
        if output in outputs:
            print(a)
            print(b)
            print(mapping)
            raise ValueError("somehow the column map is not injective...?")
        else:
            outputs.append(output)
    return mapping


def apply_col_mapping(line, mapping):
    """applies a mapping to line, mapping defined in get_column_map()"""
    rearranged = []
    for i in range(len(line)):
        value = line[mapping[i]]
        rearranged.append(value)
    return rearranged


def get_add_map(top_line, bottom_line):
    """add_map is for when we're combining previously flipped sections
    and we need to know what to add to other sections so that the boundaries
    of flipped sections don't have discontinuities
    """    
    # variables to make writing this easier
    a = top_line
    b = bottom_line
    # what to add to each column of b to get it to match up with a "up to flips"
    add_map = {n: 0 for n in range(len(b))}  # start by assuming zero
    for i, a_i in enumerate(a):
        b_i = b[i]
        dist = b_i - a_i    
        # the difference between a and b should be no larger than 50, for sure
        while abs(dist) > 50:
            if dist > 0:  # b > a so reduce b
                b_i -= 180
            else:  # b < a so increase b
                b_i += 180
            dist = b_i - a_i
        add_amount = b_i - b[i]
        add_map[i] = add_amount
    return add_map


def apply_add_mapping(line, mapping):
    """apply map generated in get_add_map() to a line"""
    new_line = [line[i] + mapping[i] for i in range(len(line))]
    return new_line


def flip_columns(sections):
    """take a list of sections and return those same sections, but with
    the columns re-ordered so they're consistent throughout megasections.
    """
    big_flipped_sections = []
    while len(sections) > 1:   
        # get the bottom section and next lowest one
        # we go bottom up since then it combines in a nicer way
        top_section = sections[-2]
        bottom_section = sections[-1]    
        # lines at the interface
        top_line = top_section[-1]
        bottom_line = bottom_section[0]
        # if the top section is bigger, it isn't related
        if len(top_line) > len(bottom_line):
            big_flipped_sections.append(bottom_section)
            # and remove last entry from the sections list
            sections.pop()
        else:
            bottom_line_segment = bottom_line[:len(top_line)]
            # find the column mapping between sections
            mapping = get_column_map(top_line, bottom_line_segment)
            # mapping has same number of keys as top_line

            # note that we can't rely on the size of bottom_line to be constant
            # so adjust the mapping as needed
            max_bottom = max([len(line) for line in bottom_section])
            for i in range(len(mapping.keys()), max_bottom):
                mapping[i] = i
            # now mapping has same number of keys as the biggest bottom_line

            # then map the bottom section so it matches top section's order
            new_bottom_section = top_section
            for line in bottom_section:
                new_bottom_section.append(apply_col_mapping(line, mapping))

            # the new lowest section is the combination of bottom and 2nd-lowest
            # but now they have the same order
            sections[-2] = new_bottom_section
            sections.pop()  # remove last index

    if len(sections) == 1:
        big_flipped_sections.append(sections[0])
        sections.pop()
    else:
        raise ValueError("How has this happened?")
       
    assert sections == []

    # sections is just one section now
    # so re-separate into sections
    list_of_lines = []
    for sect in reversed(big_flipped_sections):
        for line in sect:
            list_of_lines.append(line)
    return separate_into_sections(list_of_lines)


def flip_all_sections(sections):
    """perform flipping operation on each section and make sure that there
    are no discontinuities at section breaks within megasections"""
    # flip each section individially
    sections = [flip_one_section(section) for section in sections]
    
    # now all we have to worry about is the interfaces
    while len(sections) > 1:   
        # get the bottom section and next lowest one
        top_section = sections[-2]
        bottom_section = sections[-1]    
        # lines at the interface
        top_line = top_section[-1]
        bottom_line = bottom_section[0]

        # if the top section is bigger, it isn't related,
        # so we don't worry about it
        if len(top_line) > len(bottom_line):
            new_bottom_section = top_section + bottom_section
        else:
            # find the mapping between sections
            # (how much to add to each col of bottom)
            mapping = get_add_map(top_line, bottom_line)

            # note that we can't rely on the size of bottom_line to be constant
            # so adjust the mapping as needed
            max_bottom = max(len(line) for line in bottom_section)
            for i in range(len(mapping.keys()), max_bottom):
                mapping[i] = 0

            # then map the bottom section so it matches top section
            new_bottom_section = top_section
            for line in bottom_section:
                new_bottom_section.append(apply_add_mapping(line, mapping))
            
        # the new lowest section is the combination of bottom and 2nd-lowest
        # but now they have the same order
        sections[-2] = new_bottom_section
        sections.pop()  # remove last index
    
    # sections is just one section now
    # so re-separate into sections
    list_of_lines = sections[0]
    return separate_into_sections(list_of_lines)


def start_from_zero(sections):
    """ensure that all channels start at zero"""
    
    # get megasections
    mega_sections = separate_into_megasections(sections)
    
    for ms in mega_sections:
        num_cols = max(len(line) for line in ms)
        
        # find first element in each column
        first_elements = [None for _ in range(num_cols)]
        for line in ms:
            for i in range(num_cols):
                if (first_elements[i] is None) and (i < len(line)):
                    first_elements[i] = line[i]
            if all(x is not None for x in first_elements):
                break
        # now subtract that from every other member
        for i in range(len(ms)):
            line = ms[i]
            for j in range(len(line)):
                if j == 0:  # don't mess with the energies!
                    continue
                line[j] = line[j] - first_elements[j]
            ms[i] = line
    
    # now stitch all the megasections back into a list of lists of numbers
    list_of_lines = []
    for ms in mega_sections:
        for line in ms:
            list_of_lines.append(line)

    # and return in section format
    return separate_into_sections(list_of_lines)


def flip(read_filename):
    """performs flipping operation from start to finish"""
    print("Flipping...\r", end="")
    read_filename = utils.abs_path(read_filename)
    # read from original file
    text_lines, number_lines = sanitize(read_filename)
    
    # perform operations to get desired data
    sections = separate_into_sections(number_lines)
    sections = flip_columns(sections)
    sections = flip_all_sections(sections)
    sections = start_from_zero(sections)
    
    # write to another file
    new_filename = write_data(sections, text_lines, read_filename)

    print("Your data has been flipped! Output:", new_filename)
    return new_filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Flipper")
    parser.add_argument(
        "-f", nargs='?', const=None, help="full path to file", type=str)
    args = parser.parse_args()
    if args.f is not None:
        flip(args.f)
    else:
        flip(filepath)

