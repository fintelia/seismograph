#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors, cm
from matplotlib.ticker import PercentFormatter
import pathlib, json, glob, os
from scipy import stats
import random
import sys

class Trace:
    """Decoded data from a trace file"""

    def __init__(self, filename):
        self.times = [[], []]
        self.uops = [[], []]
        self.counter = [[], []]
        with open(filename) as file:
            data = json.load(file)
            n = 0
            for p in data["data"]:
                if p["uops_retired"] < 600 or True:
                    i = 0
                else:
                    i = 1

                if n < 10000:
                    n += 1
                    continue

                #self.times[i].append(float(p["average_cycles"])/2.4 + random.random() - 0.5)
                self.times[i].append(p["average_cycles"])
                self.uops[i].append(p["uops_retired"])
                self.counter[i].append(p["counter"])


if len(sys.argv) < 3:
    print("Expected 2+ arguments, got {}".format(sys.argv-1))
    sys.exit()

traces = []
for file in sys.argv[1:]:
    traces.append(Trace(file))

fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .4))
for i in range(2):
    axs[i].hist(traces[i].times[0], bins=35, range=(50, 120), label="uops_issued < 600")
    #axs[i].hist(traces[i].times[1], bins=300, range=(20, 50), label="uops_issued ≥ 600")
    axs[i].set_xlabel('time (ns)')
    #axs[i].legend()
axs[0].set_title("mitigations=auto")
axs[1].set_title("mitigations=off")
axs[0].set_ylabel('frequency')
plt.yscale('log', nonposy='clip')
plt.ylim(2, 10000000)

# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
# axs.scatter(times[0], counter[0], s=0.01)
# axs.scatter(times[1], counter[1], s=0.01)
# plt.ylim(np.percentile(counter[0] + counter[1], 0.1) * 0.7, np.percentile(counter[0] + counter[1], 99.9) * 1.3)
# #plt.xlim(0, np.percentile(times[0] + times[1], 99.9) * 2.3)
# plt.xlim(0, 1000)
# axs.set_xlabel('getpid time (ns)')

plt.show()

