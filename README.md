# ncsmc_resonance_finder

Python modules to help process eigenphase_shift files and find resonances

Main script is `resonance_finder.py`.

You feed it a filename (full path), and it'll do a few things:
- create a new file in the same directory as the first, with "_flipped" at the end.
  - This file has columns rearranged and phases flipped if needed.
  - (when I say flipped I mean "with no large jumps from numerical overflow, e.g. from 89 to -89")
- Then it'll read through each channel and look for resonances.
  - it'll tell you where each one is (e.g. "6-0 column 3")
  - type of resonances = "strong": >90 degrees, "possible": > 60 degrees
  - it'll make plots of strong resonances
    - (and save those in the `resonances` directory, created when script is run)
  


## Getting Started

`git clone` this, or if you're on Cedar you can find a clone in `exch`.

`git pull origin master` to get the latest version. 

### Flipping files and finding resonances

First, run `resonance_finder.py`. There are a couple ways to do this:

- run the file like `python resonance_finder.py -f <filename>`

- open the file and change the line where you set `filepath`, then run it

Either way, a file called `resonance_info.csv` will be created in `resonances`.

### Plotting multiple channels

First, pick which resonances you want to plot. 

- If you've done the last step already,
just copy the related lines from `resonance_info.csv`.

- If you haven't, you'll need to get the info of the channels you want to plot,
then put it in the same format as in `resonance_info.csv`.
  Don't worry about the 'type' (e.g. `strong`), but put some random text there

Then, in `resonance_finder.py`, there's a big string near the top.
- it's called `channels_to_plot`
- replace that with your channels of choice
- blank lines are okay, but don't add any extra spacing to the lines that matter

Then run the function `multi_channel_plot()`.

Look near the bottom of the code for what runs if there are no CLI arguments,
and edit that behaviour. If you just put a new line somewhere else, it'll run
everytime someone tries to find resonances with a `-f` input.

Parameters:
- `filename`
  - the name of the file where we'll get channel data
- `already_flipped` (default `False`)
  - whether or not the specified file has been flipped already
  - saves time if True
- `energy_bounds` (default `(-inf, inf)`)
  - lower and upper bounds of energies to plot
- `output_type` (default `"matplotlib"`)
  - the type of output you want

### Prerequisites

Python (3.7.4 ideally, other versions may work)

`numpy` is also needed.

On cedar or a local machine, use `pip install --user numpy`
