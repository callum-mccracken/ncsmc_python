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
#bound_states = output_simplifier.simplify(ncsmc_dot_out)

# get info about all resonances in the files
#phase_csv = resonance_info.get_resonance_info(phase_flipped, Nmax=Nmax, already_flipped=True)
#eigenphase_csv = resonance_info.get_resonance_info(eigenphase_flipped, Nmax=Nmax, already_flipped=True)

# plot all channels, and make csvs for each individual channel too
#resonance_plotter.plot(phase_flipped, flipped=True, Nmax=Nmax)
#resonance_plotter.plot(eigenphase_flipped, flipped=True, Nmax=Nmax)

# then from here you have to look at the resonance images,
# and figure out which ones are interesting.

# you're looking for phase vs energy curves that look like a smooth step
# function, a sigmoid function, or I guess kind of like a sideways cubic.

# When you find those, write down their corresponding lines
# from the resonances.csv file.

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

# differently formatted version for later
phase_titles = [
    "_".join(line.split(",")[:-1]) for line in phase_channels.splitlines()]
eigenphase_titles = [
    "_".join(line.split(",")[:-1]) for line in eigenphase_channels.splitlines()]

# TODO: we should only really use one of these to figure out which
# channels have resonances, right? Which one is it?

# now re-plot the interesting ones / make a spaghetti plot with all those
phase_csvs = resonance_plotter.plot(
    phase_flipped, flipped=True, Nmax=Nmax, channels=phase_channels)
eigenphase_csvs = resonance_plotter.plot(
    eigenphase_flipped, flipped=True, Nmax=Nmax, channels=eigenphase_channels)


# now that you have these plots, use the interactive plotter thing to find the
# energy of each resonance (i.e. it's "point of inflection", note the quotes)

# TODO: I'm pretty sure we're supposed to use the other file to figure out
# where the resonances are, right?

phase_widths = []
phase_energies = []
for csv in phase_csvs:
    width, energy = fitter.find_resonance(csv)
    phase_widths.append(width)
    phase_energies.append(energy)
eigenphase_widths = []
eigenphase_energies = []
for csv in eigenphase_csvs:
    width, energy = fitter.find_resonance(csv)
    eigenphase_widths.append(width)
    eigenphase_energies.append(energy)

# save that information in files for easy access later
phase_info_path = os.path.join(utils.output_dir.format(Nmax), "phase_info.csv")
eigenphase_info_path = os.path.join(utils.output_dir.format(Nmax), "eigenphase_info.csv")
fitter.save_info(phase_info_path, phase_titles, phase_widths, phase_energies)
fitter.save_info(eigenphase_info_path, eigenphase_titles, eigenphase_widths, eigenphase_energies)



# you want to include in your actual level scheme
# you'll also need to take a look at TUNL data to figure out 
