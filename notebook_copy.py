"""a pretty-much exact copy of the mathematica notebook"""
import numpy as np
import matplotlib.pyplot as plt

# read in all eigenphases to a list
eigenphase = [1,2,3,4,5]
energies = [1,2,3,4,5]

# take a slice of the lists to use for the fit
start_index = 0
end_index = 5
x = energies[start_index:end_index]
y = eigenphase[start_index:end_index]

# find the coefficients of the cubic of best fit
d, c, b, a = np.polyfit(x, y, 3)

# the steepest point of the resonance occurs at this value of energy:
# (since it's a cubic)
steep_energy = - c / (3 * d)
print(steep_energy)

def dphase_denergy(energy):
    """derivative of phase w.r.t. energy, in radians"""
    return np.radians(b + 2*c*energy + 3*d*energy**2)

# TODO: what's this one for? Something to do with resonance width?
two_by_ddelta_er = 2 / dphase_denergy(steep_energy)
print(two_by_ddelta_er)

# make plot
plt.plot(x, y, "-g")
plt.plot(x, [a + b*x_i + c*x_i**2 + d*x_i**3 for x_i in x], "--r")
plt.show()