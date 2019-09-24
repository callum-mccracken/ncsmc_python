from flipper import flip, separate_into_channels
import matplotlib.pyplot as plt
from os.path import realpath, split, join, exists
from os import mkdir

# where we store images of resonances
this_dir = split(realpath(__file__))[0]
images_dir = join(this_dir, "resonances")

if not exists(images_dir):
    mkdir(images_dir)

def multi_strip(string, list_of_strs):
    for s in list_of_strs:
        if s == "":  # ignore this case
            continue
        while s in string:
            string = string.replace(s, "")
    return string


def find_resonances(filename):
    # first flip the file
    new_filename = flip(filename)

    # channels: dict, key = title, value = list with channel numbers
    # energy is a list of energy values
    channels = separate_into_channels(new_filename)

    # now look in each channel for a resonance
    for title, list_of_nums in channels.items():
        # we'll want a good title for plotting etc.
        nice_title = multi_strip(title, ["\n", "\\", "S", "N", "@", "legend"])
        # remove s0, s1, ..., (the first word), that's just used for xmgrace
        nice_title = nice_title[nice_title.index('"'):]
        
        resonance = False
        maybe_resonance = False

        max_difference = abs(max(list_of_nums) - min(list_of_nums))
        
        if max_difference > 60:
            maybe_resonance = True
            word = "possible"
        if max_difference > 90:
            resonance = True
            word = "strong"

        if maybe_resonance:
            print()
            print(word + " resonance detected at \n"+title)
            print()

        if resonance:
            plt.title(title)
            plt.ylabel("Phase (degrees)")
            plt.xlabel("Number in list, $\\propto$ energy")
            plt.plot(list_of_nums)
            image_title = nice_title.replace('"', "").replace(" ", "_")
            plt.savefig(join(images_dir, image_title+".png"))
            plt.clf()

if __name__ == "__main__":
    find_resonances("/Users/callum/Desktop/rough_python/ncsmc/to_be_flipped/big_eigenphase_shift.agr")
