import flipper
import output_simplifier
import resonance_info
import resonance_plotter
import gui_fitter
#import pheno
import scheme_plot
import utils

import os

# name of phase shift file, ensure it exists
phase_shift = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/phase_shift.agr"
eigenphase_shift = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/eigenphase_shift.agr"
ncsmc_dot_out = "/Users/callum/Desktop/rough_code/ncsmc_resonance_finder/ncsmc_output/ncsm_rgm_Am2_1_1.out"
Nmax = 4

for f in [phase_shift, eigenphase_shift, ncsmc_dot_out]:
    if not os.path.exists(f):
        raise IOError("file "+f+" does not exist!")
    if not os.path.getsize(phase_shift) > 0:
        raise ValueError("file "+f+" is empty!")

# flip the files, assuming we don't have to rearrange columns at all
phase_flipped = flipper.flip(phase_shift)
eigenphase_flipped = flipper.flip(eigenphase_shift)

# make simplified output file, and return energies of bound states
bound_states = output_simplifier.simplify(ncsmc_dot_out)

# get info about all resonances in the files
phase_csv = resonance_info.get_resonance_info(phase_flipped, Nmax=Nmax, already_flipped=True)
eigenphase_csv = resonance_info.get_resonance_info(eigenphase_flipped, Nmax=Nmax, already_flipped=True)

# plot all channels, and make csvs for each individual channel too
resonance_plotter.plot(phase_flipped, flipped=True, Nmax=Nmax)
resonance_plotter.plot(eigenphase_flipped, flipped=True, Nmax=Nmax)

# then from here you have to look at the resonances,
# and figure out which ones are interesting.

interesting_phase = """


"""


# you want to include in your actual level scheme
# you'll also need to take a look at TUNL data to figure out 



