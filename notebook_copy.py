"""a pretty-much exact copy of the mathematica notebook"""
import numpy as np
import matplotlib.pyplot as plt

# read in all eigenphases to a list
# eignphase = ReadList["filename", Number, RecordLists -> True];
eigenphase = [1,2,3,4,5]
energies = [1,2,3,4,5]

# take a slice of that list to use for the fit
# fit = eignphase[[40;;70]];
start_index = 40
end_index = 70
phases_to_consider = eigenphase[start_index:end_index]
energies_to_consider = energies[start_index:end_index]

# translate to x, y terminology to match up with notebook
x = energies_to_consider
y = phases_to_consider

# find the coefficients of the cubic of best fit
# resfit = FindFit[fit, a + bx + cx^2 + dx^3, {a, b, c, d}, x]
a, b, c, d = np.polyfit(x, y, 3)

# define ddelta, which means [...]
# TODO: what does it mean? It's proportional to the derivative of the fit
# ddelta[x_] = (b + 2cx + 3dx^2) Pi / 180 /.%
def ddelta(x):
    return np.pi / 180 * (b + 2*c*x + 3*d*x**2)

# plot the ddelta values for the x we have
# Plot[ddelta[x], {x, .8, 1.5}]
plt.plot(x, [ddelta(x_i) for x_i in x])
plt.show()

# er? TODO: what in the heck is er?
# er = -c / (3.0 * d) /. resfit
er = -c / (3 * d)
print(er)

# TODO: what's this one for too?
# 2 / ddelta[er]
two_by_ddelta_er = 2 / ddelta(er)
print(two_by_delta_er)

# make final plot
# Show[Plot[a + bx + cx^2 + dx^3 /. resfit, {x, .9, 1.3}], ListPlot[fit]]
plt.plot(x, y, "-g")
plt.plot(x, [a + b*xi + c*xi^^2 + d*xi**3 for xi in x], "--r")
plt.show()