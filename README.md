# ncsmc_python

Python modules to help process NCSMC phase shift files and find resonances.

There are a few useful scripts, which can all be run with `python -f [path]`,
where `[path]` is a (possibly relative) path to a NCSMC phase shift file.

You'll likely want to run `resonance_plotter.py` most often.

## flipper.py

This script takes your NCSMC phase shift output and creates a new file
in the same directory as the first, with "_flipped" at the end.

- This file has columns rearranged and phases flipped wherever needed
  (when I say flipped I mean "with no large jumps, e.g. from 89 to -89").
- It also replaces `NaN` values with `0`.
- Other than those points above, the structure of the file is exactly the same
  as a NCSMC phase shift file.

## resonance_info.py

This script extends the functionality of `flipper.py`.

In addition to flipping, it creates a spreadsheet (`.csv` file) containing
information about channels, and which ones might be resonances.

## resonance_plotter.py

This extends `resonance_info.py`.

It flips, finds resonance info, and then plots each resonance.

- By default, plots are only made for `strong` resonances, 
  but that's easy to edit if you open `resonance_plotter.py` and edit one variable
  (`res_types`).

## output_simplifier.py

Takes ncsmc output (.out) files, grabs info about bound states,
and outputs a ".out_simplified" file in the same spot as the original.

## Getting Started

`git clone` this, or if you're on Cedar you can find a clone in `exch`.

`git pull origin master` to get the latest version. 


### Prerequisites

Python (3.7.4 ideally, other versions may work)

`numpy` and `matplotlib` are also needed, for numerical analysis and plotting functions.

On most machines, `pip install --user numpy` (then do `matplotlib`) should work.
