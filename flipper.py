"""
Flipper

Contains a whole bunch of functions which...

- read ncsmc phase shift output files

- clean them up for processing

- remove unphysical jumps in the data caused by "wrapping"
  (e.g. -89.8, -89.9, 89.9)

- reorder columns so that they are consistent as one scrolls down

- (that was deprecated, but the functions still exist)

- allow you to pick out individual channels

This module can be run with

python flipper.py -f /path/to/some/file (assumes file is not already flipped)

(output is saved in the same spot as the input, with _flipped at the end)

"""
import argparse

import numpy as np

import utils

filepath = "/path/to/eigenphase_shift.agr"


def flip_if_needed(top_nums, btm_nums):
    """
    Compare every number in top_nums to every one in btm_nums.
    If the difference is big, flip the number to make it small.

    By "flip", I mean add or subtract 180, as needed.

    Return the new list of nums, after being flipped if needed

    """
    # the threshold of "that difference is not real data, that's flipped"
    # value = arbitrary, but if we set it too high it can be a problem
    thresh = 90

    for i in range(len(top_nums)):  # there might be more new nums than old
        diff = top_nums[i] - btm_nums[i]
        if abs(diff) > thresh:
            btm_nums[i] += np.sign(diff) * 180
    return btm_nums


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
    """
    Returns sections of the file based on line length

    e.g. if your file looks like
    [[1, 2], [1, 2], [1, 2, 3, 4], [1, 2, 3, 4]]

    then this will return

    [[[1, 2], [1, 2]], [[1, 2, 3, 4], [1, 2, 3, 4]]]

    I do realize some sections might have the same lengths, one after the other
    (especially at the interface between megasections) and that is dealt with.

    """
    # list_of_nums is a list of lists of numbers,
    # from the file but not formatted as strings anymore
    sections = []
    section = []
    last_line = []

    # the list at the end ensures that we save the last section
    for line in list_of_nums + [[0]]:
        if len(line) == len(last_line):
            if line[0] > last_line[0]:  # try to append line
                section.append(line)
            else:  # but if the energy dropped, we have a new section
                if section != []:
                    sections.append(section)
                section = [line]
        else:
            if section != []:  # no sense keeping sections with no lines
                sections.append(section)
            section = [line]
        last_line = line

    # check that section creation worked:
    for section in sections:
        top = section[0]
        bottom = section[-1]
        if not (len(top) == len(bottom)):
            raise ValueError("Why does section have different length lines?")

    return sections


def separate_into_megasections(sections):
    """
    Maybe calling them megasections was a little dramatic,
    but megasections are the sections of the input file separated by titles,
    rather than sections, which are separated by changing line length

    e.g. the input looks like:
    [[[1, 2], [1, 2]], [[1, 3, 4, 6]],[[1, 2]]]
    --> the megasections are:

    [[[1, 2],[1, 2],[1, 3, 4, 6]],[[1, 2]]]

    When combining sections, also make sure that energy is monotonic
    throughout a megasection!

    """
    # make mega_sections (combine sections of increasing size)
    mega_sections = []
    while len(sections) > 1:
        top_section = sections[-2]
        bottom_section = sections[-1]
        # lines at the interface
        top_line = top_section[-1]
        bottom_line = bottom_section[0]
        length_change = len(top_line) > len(bottom_line)
        energy_change = top_line[0] > bottom_line[0]
        if length_change or energy_change:
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
    """
    Returns channels (i.e. individual columns within megasections)
    as lists of floats, along with their associated labels (strings).

    Also returns energies associated with each row. Note that not all
    channels have the same length as the energy list!
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
                # if the energy (first entry) in top > energy in bottom,
                # add a text line
                if top_line[0] > bottom_line[0]:
                    # next title and "&" (2 lines)
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

    map ={0: index0, 1: index1, ...}

    so if you're wondering what column in the top line corresponds
    to which one in the bottom line, you can use this mapping.

    To apply a column mapping easily, use apply_col_mapping()

    but the ideas is that you just say you just say

    a = top line
    b = bottom line
    map = get_column_map(a, b)
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
    """
    Applies a column mapping to a line, mapping defined in get_column_map()
    """
    rearranged = []
    for i in range(len(line)):
        value = line[mapping[i]]
        rearranged.append(value)
    return rearranged


def get_add_map(top_line, bottom_line):
    """
    An add_map is for when we're combining previously flipped sections
    and we need to know what to add to other sections so that the boundaries
    of flipped sections don't have big jumps due to fixing flipping issues.

    Same kind of idea as get_column_map()
    """
    # what to add to each column of bottom_line
    # to get it to match up with top_line "up to flips"
    add_map = {n: 0 for n in range(len(bottom_line))}  # start by assuming zero
    for i, top_i in enumerate(top_line):
        bottom_i = bottom_line[i]
        diff = bottom_i - top_i
        # the absolute difference should be no larger than 50, for sure
        while abs(diff) > 50:
            if diff > 0:  # bottom > top so reduce bottom
                bottom_i -= 180
            else:  # bottom < top so increase bottom
                bottom_i += 180
            diff = bottom_i - top_i
        add_amount = bottom_i - bottom_line[i]
        add_map[i] = add_amount
    return add_map


def apply_add_mapping(line, mapping):
    """
    apply map generated in get_add_map() to a line
    """
    new_line = [line[i] + mapping[i] for i in range(len(line))]
    return new_line


def flip_columns(sections):
    """
    Take a list of sections and return those same sections, but with
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

            # the new lowest section is the combination of
            # bottom and 2nd-lowest, but now they have the same order
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
    """
    Perform flipping operation on each section and make sure that there
    are no discontinuities at section breaks within megasections
    """
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
    """
    Ensure that all channels start "from zero",
    or rather that they don't start at like 180 or -180 or something.

    Make them start from, say, 0.1, not 180.1
    """

    # get megasections
    mega_sections = separate_into_megasections(sections)

    for ms in mega_sections:
        num_cols = max(len(line) for line in ms)

        # find how much we must add / subtract to each column
        # (multiples of 180)
        first_nums = [None for _ in range(num_cols)]
        to_add = [None for _ in range(num_cols)]
        for line in ms:
            for i in range(num_cols):
                if (to_add[i] is None) and (i < len(line)):
                    # get how many 180s we have to add to get close to zero
                    to_add[i] = - int(line[i] / 180) * 180
                    first_nums[i] = line[i]
            if all(x is not None for x in to_add):
                break
        # now add that to every member of list
        for i in range(len(ms)):
            line = ms[i]
            for j in range(len(line)):
                if j == 0:  # don't mess with the energies!
                    continue
                line[j] = line[j] + to_add[j]
            ms[i] = line

    # now stitch all the megasections back into a list of lists of numbers
    list_of_lines = []
    for ms in mega_sections:
        for line in ms:
            list_of_lines.append(line)

    # and return in section format
    return separate_into_sections(list_of_lines)


def flip(read_filename, verbose=True):
    """
    Performs flipping operation from start to finish,
    returns the filename of the flipped file
    """
    if verbose:
        print("Flipping...\r", end="")
    read_filename = utils.abs_path(read_filename)
    # read from original file
    text_lines, number_lines = sanitize(read_filename)

    # perform operations to get desired data
    sections = separate_into_sections(number_lines)
    # (apparently the column issue has been solved, no need to flip cols)
    # sections = flip_columns(sections)
    sections = flip_all_sections(sections)
    # "start from zero" = make sections start within -180 --> 180
    sections = start_from_zero(sections)

    # write to output file
    new_filename = write_data(sections, text_lines, read_filename)

    if verbose:
        print("Your data has been flipped! Output:", new_filename)
    return new_filename


if __name__ == "__main__":
    # all this stuff is here so you can run this with the -f flag
    parser = argparse.ArgumentParser("Flipper")
    parser.add_argument("-f", nargs='?', const=None, help="filepath", type=str)
    args = parser.parse_args()
    if args.f is not None:
        flip(args.f)
    else:
        # if no -f flag is provided, do this.
        flip(filepath)
