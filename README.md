# ncsmc_python

Python modules to help process NCSMC output files, find resonances, and make level scheme plots.

## Summary

The most top-level module, that you'll likely run most often, is `process_ncsmc_output.py`.

Below is a quick summary of what each module does, but open each module and check out their docstrings for more details. 

- `fitter.py`: uses a GUI to help you find the widths and energies of resonances
- `flipper.py`: given a NCSMC (eigen)phase shift file, produces a "flipped" version, with no more jumps from 89 to -89
- `output_simplifier.py`: given a NCSMC `.out` file, produces a simplified version, containing only the most useful info about bound states
- `pheno.py`: a module for dealing with phenomenological adjustments, still experimental
- `process_ncsmc_output.py`: a module for dealing with NCSMC (eigen)phase files and `.out` files, calls a bunch of other modules and walks you through the process of making a level scheme plot
- `rename_post_ncsmc.py`: renames files produced after running NCSMC, can be called using a batch script
- `resonance_info.py`: given an NCSMC (eigen)phase shift file, plots and classifies all resonances
- `resonance_plotter.py`: contains functions for making resonance (spaghetti) plots
- `scheme_plot.py`: for making plots of level schemes, with single or multiple values of Nmax
- `utils.py`: various functions for making titles, etc., so we don't clutter the other modules

You won't need to worry about most modules, but note that you can run some (e.g. `flipper.py`) with a filename, like

`python flipper.py -f /path/to/file.agr`. Same deal with `resonance_info.py`, `resonance_plotter.py`, and `output_simplifier.py`.


## Getting Started

`git clone` this, or if you're on Cedar you can find a clone in `exch`.

`git pull origin master` to get the latest version. 


### Prerequisites

Python (3.7.4 ideally, other versions may work)

`numpy` and `matplotlib` are also needed, for numerical analysis and plotting functions.

On most machines, `pip install --user numpy` (then `matplotlib`) should work.

When using some interactive plotting functions, you may run into latency issues using X11 forwarding.
For this reason, when fitting resonances etc., I recommend copying NCSMC output files onto a local machine
and running this code locally.
