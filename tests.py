import flipper
import output_simplifier
import resonance_info
import resonance_plotter
import fitter
#import pheno
import scheme_plot
import utils

import os

# name of needed files
phase_shift = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/phase_shift.agr"
eigenphase_shift = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/eigenphase_shift.agr"
ncsmc_dot_out = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/ncsm_rgm_Am2_1_1.out"
Nmax = 4

# ensure files exist and are not empty
for f in [phase_shift, eigenphase_shift, ncsmc_dot_out]:
    if not os.path.exists(f):
        raise IOError("file "+f+" does not exist!")
    if not os.path.getsize(phase_shift) > 0:
        raise ValueError("file "+f+" is empty!")

# flip the files, assuming we don't have to rearrange columns at all
phase_flipped = flipper.flip(phase_shift)
eigenphase_flipped = flipper.flip(eigenphase_shift)

# make simplified output file, and return energies of bound states
bound_energies, bound_titles = output_simplifier.simplify(ncsmc_dot_out)


# get info about all resonances in the files
phase_csv = resonance_info.get_resonance_info(phase_flipped, Nmax=Nmax, already_flipped=True)
eigenphase_csv = resonance_info.get_resonance_info(eigenphase_flipped, Nmax=Nmax, already_flipped=True)

# plot all channels, and make csvs for each individual channel too
#resonance_plotter.plot(phase_flipped, flipped=True, Nmax=Nmax)
#resonance_plotter.plot(eigenphase_flipped, flipped=True, Nmax=Nmax)

# then from here you have to look at the resonance images,
# and figure out which ones are interesting.

# you're looking for phase vs energy curves that look like
# a sigmoid function, or I guess kind of like a cubic near the bend.

# When you find those, write down their corresponding lines
# from the resonances.csv file.

# make sure to look in both files, they may not look the same in both.

# one line per \n please
phase_channels = """1,-,3,4,possible
3,-,3,2,none
3,+,3,1,strong
3,+,3,3,strong
5,-,3,4,none
5,+,3,4,strong
"""

eigenphase_channels = """3,+,3,1,strong
3,+,3,2,strong
5,-,3,2,possible
5,+,3,1,strong
7,-,3,1,strong
"""

# merge those lists
all_str = eigenphase_channels + phase_channels
all_channels = "\n".join(set(all_str.splitlines()))
print(all_channels)

# differently formatted version for later
channel_titles = [
    "_".join(line.split(",")[:-1]) for line in all_channels.splitlines()]

# now use eigenphase file to find details about resonances

# now re-plot the interesting ones / make a spaghetti plot with all those
eigenphase_csvs = resonance_plotter.plot(
    eigenphase_flipped, flipped=True, Nmax=Nmax, channels=all_channels)

# path to save channel info
eigenphase_info_path = os.path.join(utils.output_dir.format(Nmax), "eigenphase_info.csv")

if not os.path.exists(eigenphase_info_path):
    # find the energy of each resonance
    # (i.e. point of highest slope within the "upward swoop")
    eigenphase_widths = []
    eigenphase_energies = []
    for csv in eigenphase_csvs:
        width, energy = fitter.find_resonance(csv)
        eigenphase_widths.append(width)
        eigenphase_energies.append(energy)
    # save that information in files for easy access later
    fitter.save_info(eigenphase_info_path, channel_titles, eigenphase_widths, eigenphase_energies)
else:
    eigenphase_widths, eigenphase_energies = [], []
    with open(eigenphase_info_path, "r+") as open_csv:
        lines = open_csv.readlines()[1:]
    for line in lines:
        _, width, energy = line.split(",")
        eigenphase_widths.append(width)
        eigenphase_energies.append(energy)

eigenphase_energies = [float(e) for e in eigenphase_energies]
eigenphase_widths = [float(e) for e in eigenphase_widths]

# you want to include in your actual level scheme
# you'll also need to take a look at TUNL data to figure out

scheme_plot.plot_multi_levels(
    [eigenphase_energies + bound_energies],
    [eigenphase_widths + [0]*len(bound_energies)],
    [channel_titles + bound_titles],
    ["$4\\hbar\\omega$"])