#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors, cm
from matplotlib.ticker import PercentFormatter
import pathlib, json, glob, os
from scipy import stats

newest_trace = max(glob.glob('trace/*'), key=os.path.getctime);
output_file = newest_trace.replace("trace/", "graphs/").replace(".json", ".png")
print("Plotting '{}' -> '{}'".format(newest_trace, output_file))

times = []
counter = []
with open(newest_trace) as file:
    data = json.load(file)
    for p in data["data"]:
        times.append(p["average_cycles"]/3.7)
        counter.append(p["counter"])

print(60, stats.percentileofscore(times, 60.01))
print(70, stats.percentileofscore(times, 70.01))
print(80, stats.percentileofscore(times, 80.01))
print(160, stats.percentileofscore(times, 160.01))

fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
axs.hist(times, bins=50, range=(0, 500))
#plt.yscale('log', nonpositive='clip')
axs.set_ylabel('frequency')
axs.set_xlabel('time (ns)')
axs.axvline(np.percentile(times, 99.9), color="black")

# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
# axs.hist(times, bins=int(np.percentile(times, 99.9)/10), range=(0, np.percentile(times, 99.9)))
# plt.yscale('log', nonpositive='clip')
# axs.set_ylabel('frequency')
# axs.set_xlabel('time (ns)')

# counter_range = (np.percentile(counter, 0.1), np.percentile(counter, 99.9))
# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
# axs.hist2d(times, counter, bins=(128, 9*8), range=((0, np.percentile(times, 99.9)), counter_range), norm=colors.LogNorm(), cmin=len(times)*0.0001)
# axs.set_ylabel('cache misses')
# axs.set_xlabel('time (cycles)')

# color_min = np.percentile(counter, 10.0)
# color_max = np.percentile(counter, 90.0)
# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
# #axs.scatter(range(len(times)), times, c=counter, s=0.1, norm=colors.Normalize(color_min, color_max, clip=True), cmap=plt.get_cmap('cividis'), label="times")
# axs.scatter(counter, times, s=0.001)
# plt.xlim(0, np.percentile(counter, 99.9));
# plt.ylim(min(times)-1, np.percentile(times, 99.99));
# axs.set_ylabel('Average getpid time (cycles)')
# axs.set_xlabel('Sample number')

pathlib.Path("graphs").mkdir(exist_ok=True)
plt.savefig(output_file)
plt.show()

