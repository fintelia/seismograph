#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import pathlib, json, glob, os

newest_trace = max(glob.glob('trace/*'), key=os.path.getctime);
output_file = newest_trace.replace("trace/", "graphs/").replace(".json", ".png")
print("Plotting '{}' -> '{}'".format(newest_trace, output_file))

times = []
frequencies = []
with open(newest_trace) as file:
    data = json.load(file)
    for p in data["data"]:
        times.append((p["average_time"] * 1000000000.0))
        frequencies.append(p["cpu_frequency"])

# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
# axs.hist2d(times, frequencies, bins=(100,30), range=((60, 100), (2000000, 5000000)), norm=colors.LogNorm())

# axs.set_ylabel('frequency')
# axs.set_xlabel('time (ns)')

# pathlib.Path("graphs").mkdir(exist_ok=True)
# plt.savefig(output_file)
# plt.show()







fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
axs.scatter(range(len(times)), times, c=frequencies, s=0.0001, norm=colors.Normalize(2000000, 5000000, clip=True), label="times")
# plt.xlim(0, 100);
plt.ylim(min(times)-.1, np.percentile(times, 99.5));
axs.set_ylabel('Average getpid time (ns)')
axs.set_xlabel('Sample number')
plt.show()

