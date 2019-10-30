"""
module to do phenomenological adjustment of data

i.e. it'll mess with your coupling kernel files
"""
from os.path import relpath, dirname, join, realpath, split, exists
import os
import shutil
import numpy as np

# NOTE: All energies in here are in MeV!

# define a channel to mess with
J = 1
J2 = J * 2
parity = -1  # 1 or -1
T = 0

# bound state or resonance? We could in theory figure this out,
# depends how big our adjustments will be though...

# data from TUNL
tunl_E = 10.847  # above ground state energy

# TODO: can we auto-generate this filename?
this_dir = dirname(__file__)
batch_file = "../runaem0105.sh"
coupling_kernels_file = "../C12_B11_coupling_kernels_Nmax06_81314_10n_4n.dat"
rgm_kernels_file = "../B11_RGM_kernels_Nmax06_81314_4n.dat"
dot_out_file = "../ncsm_rgm_Am2_1_1.out"
input_file = "../ncsm_rgm_Am2_1_1.in"
exe_file = "../ncsm_rgm_Am3_3_plus_Am2_1_1_rmatrix_ortg_omp_mpi.exe"


def get_current_state_energy(coupling_file):
    cpl_file = join(this_dir, coupling_file)
    # get current value of state energy
    with open(cpl_file, "r+") as kernels:
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

    # make sure we found at least one channel
    if len(possible_channels) == 0:
        raise ValueError("Channel with J, T, parity not found!")

    # find which line had the lowest energy
    line_num = 0
    min_E = 1e100  # filler, we'll find real value soon
    for _, _, E_i, i in possible_channels:
        if E_i < min_E:
            min_E = E_i
            line_num = i
    return min_E, line_num

def get_ground_state_energy(dot_out_file):
    dot_out_file = join(this_dir, dot_out_file)
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

def make_run_dir(new_energy, old_energy, line_num):
    """put all necessary files in a run directory"""
    # first off make the dir
    e_str = "{:05f}".format(new_energy).replace(".", "_").replace("-", "neg_")
    run_dir = join(this_dir, "E_"+e_str)
    # if it exists delete it
    if exists(run_dir):
        shutil.rmtree(run_dir)
    os.mkdir(run_dir)

    # copy exe
    current_exe = realpath(join(this_dir, exe_file))
    new_exe = join(run_dir, split(exe_file)[-1])
    shutil.copyfile(current_exe, new_exe)

    # copy rgm kernels
    current_rgm = realpath(join(this_dir, rgm_kernels_file))
    new_rgm = join(run_dir, split(rgm_kernels_file)[-1])
    shutil.copyfile(current_rgm, new_rgm)

    # copy coupling kernels and adjust the value in the new file
    current_coupling = realpath(join(this_dir, coupling_kernels_file))
    new_coupling = join(run_dir, split(coupling_kernels_file)[-1])
    shutil.copyfile(current_coupling, new_coupling)
    with open(new_coupling, "r+") as coupling:
        lines = coupling.readlines()
    line = lines[line_num]
    lines[line_num] = line.replace(str(old_energy), str(new_energy))
    with open(new_coupling, "w+") as coupling:
        coupling.writelines(lines)
    
    # copy and adjust input file so that the lines for 
    # J2min_in, J2_max_in, parity_min_in, parity_max_in
    # match the values we care about here
    current_input = realpath(join(this_dir, input_file))
    new_input = join(run_dir, split(input_file)[-1])
    shutil.copyfile(current_input, new_input)
    with open(new_input, "r+") as input_f:
        lines = input_f.readlines()
    # lines 10, 11, 12, 13 are the ones we care about
    for value, index in [(J2, 10), (J2, 11), (parity, 12), (parity, 13)]:
        # replace the current value with the new value, then rejoin line
        line = lines[index]
        words = line.split()
        words[0] = str(value)
        line = " ".join(words) + "\n"
        lines[index] = line
    with open(new_input, "w+") as input_f:
        input_f.writelines(lines)

    # copy batch file but change run directory
    current_batch = realpath(join(this_dir, batch_file))
    new_batch = join(run_dir, split(batch_file)[-1])
    shutil.copyfile(current_batch, new_batch)
    with open(new_batch, "r+") as batch:
        lines = batch.readlines()
    cd_line = 0
    for index, line in enumerate(lines):
        words = line.split()
        if "cd" in words:
            cd_line = index
            break
    if cd_line == 0:
        raise ValueError("we didn't find a cd line in the batch script!")
    lines[cd_line] = "cd "+run_dir
    with open(new_batch, "w+") as batch:
        batch.writelines(lines)
    
    # that should be it! Return batch file so we can run that later
    return new_batch

# get value of lowest energy of the state we want (as well as its line number)
current_energy, line_num = get_current_state_energy(coupling_kernels_file)

# get ground state energy from .out file
ground_state_E = get_ground_state_energy(dot_out_file)

# this is the tunl value, just shifted
experiment_energy = tunl_E + ground_state_E

print("we are off by", abs(experiment_energy - current_energy), "MeV")

test_energies = np.linspace(current_energy, experiment_energy, 10)

for test_energy in test_energies:
    print("running NCSMC for E =", test_energy, "MeV")
    # make a directory with all required input files for NCSMC
    batch = make_run_dir(test_energy, current_energy, line_num)

    # run batch script
    os.system("qsub "+batch) 