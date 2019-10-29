"""

Output Simplifier

Takes ncsmc output (.out) files, grabs info about bound states,
and outputs a .out_simplified file in the same spot as the original.

Can be run by editing the filename parameter in this file,
or just running the file with the command:

python output_simplifier.py -f [filename]

"""
import argparse
import utils

# enter a filename here,
# or run this with "python output_simplifier.py -f [file]"
filename = "ncsmc_output/ncsm_rgm_Am2_1_1.out"

# edit these two if you want to change the format of the output
file_format = """Simplified View of {filename}:

{states}
=========================================================================
"""

state_format = """
=========================================================================
Energy: {E}
J: {J}
T: {T}
Parity: {parity}

Details:
{details}"""


def simplify(filename):
    """
    Makes a simpler version of ncsmc .out files,
    no more scrolling through 100000 line files!
    """

    print("Simplifying", filename)
    # get all lines from the file, as a list of strings
    with open(filename, "r+") as file_to_simplify:
        lines = file_to_simplify.readlines()

    # bound state line will look like
    # Bound state found at E_b=[energy] [unit]
    bound_state_string = "Bound state found at E_b="
    step = "looking for J and parity"
    
    # parameters for each bound state
    E, J, T, parity, details = "", "", "", "", ""

    states = []

    for line in lines:
        if step in ["looking for J and parity", "done"]:
            if "2*J=" in line and "parity=" in line:
                # the line looks like  2*J=  6    parity=-1
                # remove unncessary junk
                replaced = line.replace("2*J=", "").replace("parity=", "")
                # get the two remaining "words", separated by spaces
                Jx2, parity = replaced.split()
                J = int(Jx2)/2
                step = "looking for T"
        if step == "looking for T":
            if "2*T=" in line:
                # the line looks like  2*T= 0
                # remove unncessary junk
                Tx2 = line.replace("2*T=", "")
                T = int(Tx2)/2
                step = "looking for bound state"
        if step in ["looking for bound state", "done"]:
            if bound_state_string in line:
                # remove the initial bit, as well as extra whitespace
                E = line.replace(bound_state_string, "").strip()
                step = "looking for details"
        if step == "looking for details":
            if "i_p,p_chan,p_st" in line:
                details += line
                step = "getting details"
        if step == "getting details":
            if "i_p,p_chan,p_st" in line:
                details += line
            else:
                # save state and move on to the next one
                states.append(state_format.format(
                    E=E, J=J, T=T, parity=parity, details=details))
                # set some parameters back to "", but not all
                # since some might be the same as for the next state
                E, details = "", ""
                # back to the first step!
                step = "done"

    # ensure we ended on a good note
    if step != "done":
        raise IOError("unable to parse file correctly, exited at wrong step!")

    # write everything to a file
    if len(states) == 0:
        states = "No bound states found..."
    else:
        states = "".join(states)
    file_str = file_format.format(filename=filename, states=states)
    with open(filename+"_simplified", "w+") as out_file:
        out_file.write(file_str)
    print("Done simplifying!")
    print("Output:", filename+"_simplified")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Output Simplifier")
    parser.add_argument("-f", nargs='?', const=None, help="filepath", type=str)
    args = parser.parse_args()
    if args.f is not None:
        simplify(args.f)
    else:
        simplify(filename)
