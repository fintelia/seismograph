#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors, cm
from matplotlib.ticker import PercentFormatter
import pathlib, json, glob, os
from numpy.lib.function_base import append
from scipy import stats, fft
from scipy.fftpack import fftfreq
import scipy
import random
import sys
from collections import Counter

def main():
    newest_trace = max(glob.glob('trace/*'), key=os.path.getctime)
    if len(sys.argv) > 1:
        newest_trace = str(sys.argv[1])

    output_file = newest_trace.replace("trace/", "graphs/").replace(".json", ".png")
    print("Plotting '{}' -> '{}'".format(newest_trace, output_file))
    #output_file = newest_trace.replace("trace/", "/home/jonathan/").replace(".json", ".png")

    ips = []
    classifications = []

    times = [[], []]
    uops = [[], []]
    counter = [[], []]
    with open(newest_trace) as file:
        data = json.load(file)
        for p in data["data"]:
            # if p["kernel_ip"] != 0:
            #     classifications.append(2)
            #     ips.append(p["kernel_ip"])
            #     continue

            if p["average_cycles"] < 300 or True:
                i = 0
            else:
                i = 1

            classifications.append(i)
            times[i].append(float(p["average_cycles"])/2.4 + random.random() - 0.5)
            uops[i].append(p["uops_retired"])
            counter[i].append(p["counter"])

    # fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
    # y = [abs(x) for x in fft(times[0][4096:8192])]
    # xf = fftfreq(len(y))
    # #axs.bar(range(len(y)-1), y[1:])
    # axs.plot(xf[1:len(y)//2], y[1:len(y)//2])
    # axs.set_xticks(np.arange(0, 0.5, 0.125))
    # plt.show()
    # return


    # n = 0
    # spacing = []
    # ip_spacing = []
    # for c in classifications:
    #     if c == 1: # Slow
    #         if n != -1:
    #             spacing.append(n)
    #         n = 0
    #     elif n == -1: # waiting for re-sync
    #         pass
    #     elif c == 0: # Fast
    #         n += 1
    #     elif c == 2: # Sample taken
    #         ip_spacing.append(n)
    #         n = -1

    # ip_totals = [0, 0]
    # ip_frequency = [Counter(), Counter()]
    # expected_spacing = np.percentile(spacing, 50)
    # print("expected_spacing =", expected_spacing)
    # for (ip, spacing) in zip(ips, ip_spacing):
    #     if spacing == expected_spacing:
    #         ip_frequency[0][ip] += 1
    #         ip_totals[0] += 1
    #     else:
    #         ip_frequency[1][ip] += 1
    #         ip_totals[1] += 1

    # print(ip_totals[1], ip_totals[0])
    # print("")

    # for (ip, freq) in (ip_frequency[0] + ip_frequency[1]).most_common(30):
    #     fast = ip_frequency[1][ip] / ip_totals[1]
    #     slow = ip_frequency[0][ip] / ip_totals[0]

    #     print("{} {:>8.2f} {:>8.2f}".format(hex(ip).rjust(20), fast * 100, slow * 100))

    # a = []
    # common_ip_totals = [0, 0]
    # for (ip, freq) in (ip_frequency[0] + ip_frequency[1]).most_common(10):
    #     common_ip_totals[0] += ip_frequency[0][ip]
    #     common_ip_totals[1] += ip_frequency[1][ip]
    #     a.append([ip_frequency[0][ip], ip_frequency[1][ip]])

    # a.insert(0, [ip_totals[0] - common_ip_totals[0], ip_totals[1] - common_ip_totals[1]])

    # chi2_stat, p_val, dof, ex = stats.chi2_contingency(a)
    # print("===Chi2 Stat===")
    # print(chi2_stat)
    # print("\n")
    # print("===Degrees of Freedom===")
    # print(dof)
    # print("\n")
    # print("===P-Value===")
    # print(p_val)
    # print("\n")
    # print("===Contingency Table===")
    # print(ex)
    # print("===Original Table===")
    # print(a)

    # return

    # fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
    # axs.hist(spacing, bins=15, range=(0, 15))
    # #plt.ylim(2, 10000000)
    # axs.set_ylabel('frequency')
    # axs.set_xlabel('spacing')
    # plt.show()
    # return

    # print(60, stats.percentileofscore(times, 60.01))
    # print(70, stats.percentileofscore(times, 70.01))
    # print(80, stats.percentileofscore(times, 80.01))
    # print(160, stats.percentileofscore(times, 160.01))

    print(len(times[0]))
    print(np.median(times[0]) * 2.4)

    fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
    axs.hist(times[0], bins=500, range=(0, np.percentile(times[0], 99.9)))
    #axs.hist(times[1], bins=500, range=(0, np.percentile(times[0], 99.9)))
    #plt.yscale('log', nonposy='clip')
    #plt.ylim(2, 10000000)
    axs.set_ylabel('frequency')
    axs.set_xlabel('time (ns)')

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

    # fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .8))
    # axs.scatter(times[0], counter[0], s=0.01)
    # axs.scatter(times[1], counter[1], s=0.01)
    # plt.ylim(np.percentile(counter[0] + counter[1], 0.1) * 0.7, np.percentile(counter[0] + counter[1], 99.9) * 1.3)
    # #plt.xlim(0, np.percentile(times[0] + times[1], 99.9) * 2.3)
    # plt.xlim(0, 1000)
    # axs.set_xlabel('time (ns)')
    # #axs.set_ylabel('RESOURCE_STALLS.ANY')

    # band = np.percentile(counter2, 99.9) / 10
    # print("counter2:", min(counter2), "..", np.percentile(counter2, 99.9))
    # fig, axs = plt.subplots(2, 5, sharex=True, sharey=True, tight_layout=True, figsize=(16 * .8, 9 * .4))
    # for (j, ax) in enumerate(np.ndarray.flatten(axs)):
    #     x = [times[i] for i in range(len(times)) if counter2[i] < (j+1) * band and counter2[i] >= j * band]
    #     y = [counter[i] for i in range(len(times)) if counter2[i] < (j+1) * band and counter2[i] >= j * band]
    #     print(len(x))
    #     ax.scatter(x, y, s=0.001)
    #     ax.set_title("{:.1f}..{:.1f}".format(j * band, (j+1) * band))
    #     ax.set_ylim(0, np.percentile(counter, 99.9) * 1.3)
    #     ax.set_xlim(0, np.percentile(times, 99.9) * 1.3)
    #     # ax.set_xlabel('getpid time (ns)')
    #     # if j == 0:
    #     #     ax.set_ylabel('UOPS_ISSUED.ANY')


    pathlib.Path("graphs").mkdir(exist_ok=True)
    plt.savefig(output_file)
    plt.show()

if __name__ == "__main__":
    main()