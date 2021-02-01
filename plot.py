#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors, cm
from matplotlib.ticker import PercentFormatter
import pathlib, json, glob, os
from scipy import stats
import random

newest_trace = max(glob.glob('trace/*'), key=os.path.getctime);
output_file = newest_trace.replace("trace/", "graphs/").replace(".json", ".png")
print("Plotting '{}' -> '{}'".format(newest_trace, output_file))
#output_file = newest_trace.replace("trace/", "/home/jonathan/").replace(".json", ".png")

times = []
counter = []
with open(newest_trace) as file:
    data = json.load(file)
    for p in data["data"]:
        # if p["average_cycles"]/2.4 > 500:
        #     continue
        # if p["counter"] == 2093:
        #     continue

        times.append(float(p["average_cycles"])/2.4 + random.random() - 0.5) #
        counter.append(p["counter"])

# print(60, stats.percentileofscore(times, 60.01))
# print(70, stats.percentileofscore(times, 70.01))
# print(80, stats.percentileofscore(times, 80.01))
# print(160, stats.percentileofscore(times, 160.01))

# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
# axs.hist(times, bins=500, range=(0, 500))
# #plt.yscale('log', nonposy='clip')
# axs.set_ylabel('frequency')
# axs.set_xlabel('time (ns)')
# axs.axvline(np.percentile(times, 99.9), color="black")

# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
# axs.hist(times, bins=int(np.percentile(times, 99.9)), range=(0, np.percentile(times, 99.9)))
# plt.yscale('log', nonposy='clip')
# axs.set_ylabel('frequency')
# axs.set_xlabel('time (ns)')

counter_range = (np.percentile(counter, 0.0) * 0.9, np.percentile(counter, 99.9) * 1.3)
time_range = (np.percentile(times, 0.0), np.percentile(times, 99.9) * 1.3)
fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
axs.hist2d(times, counter, bins=(150, 250*9/16.), range=(time_range, counter_range), norm=colors.LogNorm(), cmin=1, cmap='Oranges') #
axs.set_ylabel('UOPS_ISSUED.ANY')
axs.set_xlabel('Counter Enabled Cycles')

# color_min = np.percentile(counter, 10.0)
# color_max = np.percentile(counter, 90.0)
# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
# axs.scatter(times, counter, s=0.0001) #norm=colors.Normalize(color_min, color_max, clip=True),
# # cmap=plt.get_cmap('cividis'), 
# #axs.scatter(counter, times, s=0.001)
# plt.ylim(np.percentile(counter, 0.0), np.percentile(counter, 99.9));
# plt.xlim(min(times)-1, np.percentile(times, 99.9));
# axs.set_xlabel('getpid time (ns)')
# axs.set_ylabel('UOPS_ISSUED.ANY')

pathlib.Path("graphs").mkdir(exist_ok=True)
plt.savefig(output_file)
plt.show()

