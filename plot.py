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
counter2 = []
with open(newest_trace) as file:
    data = json.load(file)
    for p in data["data"]:
        # if p["average_cycles"]/2.4 > 500:
        #     continue
        # if p["counter"] == 2093:
        #     continue

        times.append(float(p["average_cycles"]) + random.random() - 0.5) # /2.4
        counter.append(p["counter"])
        counter2.append(p["counter2"])

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

# counter_range = (np.percentile(counter, 0.0) * 0.9, np.percentile(counter, 99.9) * 1.3)
# time_range = (np.percentile(times, 0.0), np.percentile(times, 99.9) * 1.3)
# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
# axs.hist2d(times, counter, bins=(150, 250*9/16.), range=(time_range, counter_range), norm=colors.LogNorm(), cmin=1, cmap='Oranges') #
# axs.set_ylabel('counter')
# axs.set_xlabel('getpid time (ns)')

# color_min = min(counter2) #np.percentile(counter2, 10.0)
# color_max = np.percentile(counter2, 99.9)
# print("counter2:", color_min, "..", color_max)
# color_max = 8
# fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
# axs.scatter(times, counter, c=counter2, s=0.0001, norm=colors.Normalize(color_min, color_max, clip=True), cmap='Set2') #,
# # cmap=plt.get_cmap('cividis'), 
# #axs.scatter(counter, times, s=0.001)
# plt.ylim(0, np.percentile(counter, 99.9) * 1.3);
# plt.xlim(0, np.percentile(times, 99.9) * 1.3);
# axs.set_xlabel('getpid time (ns)')
# axs.set_ylabel('UOPS_ISSUED.ANY')

band = np.percentile(counter2, 99.9) / 10
print("counter2:", min(counter2), "..", np.percentile(counter2, 99.9))
fig, axs = plt.subplots(2, 5, sharex=True, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .4))
for (j, ax) in enumerate(np.ndarray.flatten(axs)):
    x = [times[i] for i in range(len(times)) if counter2[i] < (j+1) * band and counter2[i] >= j * band]
    y = [counter[i] for i in range(len(times)) if counter2[i] < (j+1) * band and counter2[i] >= j * band]
    print(len(x))
    ax.scatter(x, y, s=0.001)
    ax.set_title("{:.1f}..{:.1f}".format(j * band, (j+1) * band))
    ax.set_ylim(0, np.percentile(counter, 99.9) * 1.3)
    ax.set_xlim(0, np.percentile(times, 99.9) * 1.3)
    # ax.set_xlabel('getpid time (ns)')
    # if j == 0:
    #     ax.set_ylabel('UOPS_ISSUED.ANY')


pathlib.Path("graphs").mkdir(exist_ok=True)
plt.savefig(output_file)
plt.show()

