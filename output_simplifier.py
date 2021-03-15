"""
Takes ncsmc output (.out) files, grabs info about bound states,
and outputs a ".out_simplified" file in the same spot as the original.

Can be run by editing the filename parameter in this file,
or just running the file with the command:

``python output_simplifier.py -f [filename]``

"""
import argparse
import re

import utils

# enter a filename here,
# or run this with "python output_simplifier.py -f [file]"
filename = "/path/to/ncsm_rgm_Am2_1_1.out"

# edit these two if you want to change the format of the output
file_format = """Simplified View of {filename}:

(only includes bound states)

Threshold Energy = {thresh_E} MeV
Groud State Energy = {ground_E} MeV

{states}
=========================================================================
"""

state_format = """
=========================================================================
Bound State Energy = {E} MeV
J = {J}
T = {T}
Parity = {parity}

Details:
{details}"""


# a bunch of tiny functions for parsing data
def j_parity_line(line):
    """
    Checks if line is of the form::

        2*J=  6    parity=-1

    line:
        string, a line of a file
    """
    regex = r"[ ]*2\*J=[ ]*[-]?[0-9]*[ ]*parity=[ ]*[-]?[0-9]*\n"
    return bool(re.match(regex, line))


def get_j_parity(line):
    """
    assuming j_parity_line(line) == True, return J, parity
    
    line:
        string, a line of a file
    """
    # remove everything except necessary info
    just_nums = line.replace("2*J=", "").replace("parity=", "")
    # get the two "words", i.e. numbers, separated by spaces
    Jx2, parity = just_nums.split()
    J = int(Jx2)/2
    return J, parity


def t_line(line):
    """
    Checks if line is of the form::

        2*T= 0

    line:
        string, a line of a file
    """
    regex = r"[ ]*2\*T=[ ]*[-]?[0-9]*\n"
    return bool(re.match(regex, line))


def get_t(line):
    """
    assuming t_line(line) == True, return T

    line:
        string, a line of a file
    """
    Tx2 = line.replace("2*T=", "")
    T = int(Tx2)/2
    return T


def bound_state_line(line):
    """
    Checks if line is of the form::

        Bound state found at E_b=[energy] [unit]

    line:
        string, a line of a file
    """
    return "Bound state found at E_b=" in line


def get_e(line):
    """
    assuming bound_state_line(line) == True, return E

    line:
        string, a line of a file
    """
    # remove the initial bit, as well as extra whitespace
    with_units = line.replace("Bound state found at E_b=", "").strip()
    E = with_units.split()[0]  # first "word" = E, second = units
    return float(E)


def groud_e_line(line):
    """
    Checks if line contains ``Ground-state E=``

    line:
        string, a line of a file
    """
    return "Ground-state E=" in line


def get_ground_e(line):
    """
    *edited since ground state energy is not on
    the line that says "Ground-state E="

    The line looks like::

        Lowest eigenenergy= -68.4838 MeV

    Get E.

    line:
        string, a line of a file
    """
    # remove initial bit
    line = line.replace("Lowest eigenenergy=", "")
    # then after that, it'll be the first "word", strip whitespace too
    E = line.split()[0].strip()
    return float(E)


def thresh_e_line(line):
    """
    Checks if line contains ``Threshold E=``

    line:
        string, a line of a file
    """
    return "Threshold E=" in line


def get_thresh_e(line):
    """
    line looks like::

        Threshold E= -69.0645 MeV

    line:
        string, a line of a file
    """
    # remove the first bit, as well as any extra whitespace
    with_units = line.replace("Threshold E=", "").strip()
    E = with_units.split()[0]  # first "word" = E, second = units
    return float(E)


def simplify(filename, verbose=False):
    """
    Makes a simpler version of ncsmc .out files,
    no more scrolling through 100000 line files!

    Steps:

    1. Look for J, parity, T.
        - we may have many of these values before seeing a bound state
        - keep the most recent values before the bound state is mentioned

    2. Get bound state energy
        - there may be multiple bound states with the same J pi T,
          so don't stop looping through when we find one

    3. Get details

    filename:
        string, path to ncsmc "dot out" file

    verbose:
        boolean, whether or not to print messages
    """
    filename = utils.abs_path(filename)
    if verbose:
        print("Simplifying "+filename)
    # get all lines from the file, as a list of strings
    with open(filename, "r+") as file_to_simplify:
        lines = file_to_simplify.readlines()

    # if something went wrong, we'll see this where the right value should be
    default = "ERROR"

    # constant parameters
    ground_E, thresh_E = default, default

    # parameters for each bound state
    E, J, T, parity, details = default, default, default, default, default

    # lists to store E values and state titles, to return at the end
    E_list = []
    state_titles = []

    # this will hold strings describing states
    states = []

    # start by searching for a bound state
    step = "looking for bound state"

    # All steps:
    """
        looking for bound state
            (scanning through for "Bound state found at E_b=")
        looking for details
            (scanning for i_p,p_chan,p_st values)
        getting details
            (getting subsequent lines of i_p,p_chan,p_st values)
        Then back to looking for details or bound state until lines run out

        Collects info about each bound state and related details,
        saving in the state_format format, i.e.

        ======================================================================
        Bound State Energy = {E} MeV
        J = {J}
        T = {T}
        Parity = {parity}

        Details:
        {details}
        ======================================================================
        
        (where J, T, parity are the most recent values to appear above
        the line "Bound state found at E_b= [X] MeV")
    """

    # counter to get 2 lines down from "Ground-state E="
    gs_counter = 0
    gs_found = False

    for line in lines:
        if groud_e_line(line):
            # i.e. if line contains ``Ground-state E=``
            gs_found = True
        elif thresh_e_line(line):
            # i.e. if line contains ``Threshold E=``
            thresh_E = get_thresh_e(line)

        if gs_found:
            gs_counter += 1  # count until we find gs line
            if gs_counter == 3:  # it's 2 lines down, counter's weird
                # line contains ``Ground-state E=``
                ground_E = get_ground_e(line)
                if verbose:
                    print('ground-state E =', ground_E)
                # then reset the counter
                gs_found = False
                gs_counter = 0

        # get J, T, parity, E for bound states
        if step == "looking for bound state":
            # safe to assume that if we find a bound state, we'll find
            # J, parity, T first, so no need to make that its own step
            if j_parity_line(line):  # of the form 2*J=  6    parity=-1
                J, parity = get_j_parity(line)
                #if verbose:
                #    print('Updated J, parity:', J, parity)
            elif t_line(line):  # of the form 2*T= 0
                T = get_t(line)
                #if verbose:
                #    print('Updated T:', T)
            # then keep looking for a bound state.
            # if we find new J, parity, T values we'll update as needed

            elif bound_state_line(line):  # ``Bound state found at E_b=''
                E = get_e(line)
                if verbose:
                    print('Found bound state:', E)
                step = "looking for details"  # details: i_p,p_chan,p_st

        # get the first detail line
        elif step == "looking for details":
            if "i_p,p_chan,p_st" in line:
                details = line
                if verbose:
                    print('found first detail line')
                step = "getting details"
            elif bound_state_line(line):  # ``Bound state found at E_b=''
                if verbose:
                    print('found an additonal bound state, appending state')
                states.append(state_format.format(
                    E=E, J=J, T=T, parity=parity, details="None"))
                E_list.append(E)
                state_titles.append("{}_{}_{}".format(J, parity, T))
                E = get_e(line)
                if verbose:
                    print('Found bound state:', E)
                step = "looking for details"  # details: i_p,p_chan,p_st

        # get all other detail lines
        elif step == "getting details":
            if "i_p,p_chan,p_st" in line:
                #if verbose:
                #    print('detail line', line)
                details += line
            else:
                if verbose:
                    print('done getting details, appending state')
                # once we've found the first line after the details,
                # save state and move on to the next one
                states.append(state_format.format(
                    E=E, J=J, T=T, parity=parity, details=details))
                E_list.append(E)
                #if verbose:
                #    print('E_list appended', E)
                state_titles.append("{}_{}_{}".format(J, parity, T))
                # set some parameters back to default, but not all
                # since some might be the same as for the next state
                E, details = default, default
                # back to the first step / look for next bound state
                step = "looking for bound state"

    # ensure we didn't end part way through processing a state
    if step != "looking for bound state":
        raise IOError("unable to parse file correctly, exited at wrong step!")

    # write everything to a file
    if len(states) == 0:
        states = "No bound states found..."
    else:
        states = "".join(states)
    file_str = file_format.format(
        filename=filename,
        ground_E=ground_E,
        thresh_E=thresh_E,
        states=states)
    with open(filename+"_simplified", "w+") as out_file:
        out_file.write(file_str)
    if verbose:
        E_string = ", ".join([str(E) for E in E_list])
        print("Done simplifying! Found bound states at "+E_string)
        print("Simplified output file: "+filename+"_simplified")
    return E_list, state_titles


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Output Simplifier")
    parser.add_argument("-f", nargs='?', const=None, help="filepath", type=str)
    parser.add_argument("-v", nargs='?', const=False, help="verbose", type=bool)
    args = parser.parse_args()
    if args.f is not None:
        simplify(args.f, verbose=args.v)
    else:
        simplify(filename)
