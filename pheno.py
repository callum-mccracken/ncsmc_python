"""
module to do phenomenological adjustment of data

i.e. it'll mess with your coupling kernel files
"""
# NOTE: All energies in here are in MeV!

# define a channel to mess with
J = 1
parity = -1  # 1 or -1
T = 0

# bound state or resonance? We could in theory figure this out,
# depends how big our adjustments will be though...

# data from TUNL
tunl_E = 10.847  # above ground state energy

# get ground state energy
ground_state = -60


# get current value of state energy
# TODO: can we auto-generate this filename?
coupling_kernels_file = "C12_B11_coupling_kernels_Nmax06_81314_10n_4n.dat"
dot_out_file = "ncsm_rgm_Am2_1_1.out"

def get_current_coupling_data(coupling_file):
    with open(coupling_file, "r+") as kernels:
        kernel_lines = kernels.readlines()

    possible_channels = []
    for i, line in enumerate(kernel_lines):
        # check if it's the state we want
        # if so, it will have exactly 3 "words" (entities separated by space)
        words = line.split()
        if len(words) != 3:
            continue
        # the first word should be 2J
        file_J = int(words[0]) / 2
        if file_J != J:
            continue
        # and the second word should be 2T
        file_T = int(words[1]) / 2
        if file_T != T:
            continue

        # the third word should be the state energy
        file_E = float(words[2])

        # if we made it this far, we've found a possible channel
        possible_channels.append([file_J, file_T, file_E, i])

    # find which line had the lowest energy
    line_num = 0
    min_E = 1e100  # filler, we'll find real value soon
    for _, _, E_i, i in possible_channels:
        if E_i < min_E:
            line_num = i
    return min_E, line_num

def get_ground_state(dot_out_file):
    with open(dot_out_file, "r+") as out_file:
        lines = out_file.readlines()
    for line in lines:
        if "Ground-state E=" in line:
            """line looks like:
            Ground-state E= -68.4838  T_rel=   9.3033  [...]"""
            # remove initial bit
            line = line.replace("Ground-state E=", "")
            # then after that, it'll be the first "word", strip whitespace too
            E = line.split()[0].strip()
            # this won't ever change through the file so return the first one
            return float(E)

# now we have the line number of the line with lowest energy
# as well as the value of that energy
current_state_energy, line_num = get_current_coupling_data(coupling_kernels_file)

# get ground state E from .out file
ground_state_E = get_ground_state(dot_out_file)

# figure out how much we need to nudge it
ideal_energy = tunl_E + ground_state_E

nudges = []

for nudge in nudges:
    test_value = tunl_E + nudge
    # make a directory with all required input files for NCSMC

    # run NCSMC

# we'll analyze the output with another script