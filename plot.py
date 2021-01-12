#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import csv

cycles_all = []
with open('bench.all.csv', newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for row in r:
        cycles_all.append(float(row[1]))

cycles_none = []
cycles_none2 = []
with open('out', newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for row in r:
        cycles_none.append(float(row[1]))
        cycles_none2.append(float(row[2]))

n_bins = 50

fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)

# We can set the number of bins with the `bins` kwarg
#axs.hist(cycles_all, range=(410,470), bins=n_bins, label="mitigations=on")
axs.hist2d(cycles_none, cycles_none2, bins=(70,60), range=((430, 500), (2000000, 5000000)), label="mitigations=off", norm=colors.LogNorm())

axs.set_ylabel('frequency')
axs.set_xlabel('cycles')
axs.legend()

plt.savefig("histogram.png")
plt.show()
