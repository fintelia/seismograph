#!/bin/python3

from matplotlib import colors, cm
from matplotlib.ticker import PercentFormatter
from scipy import stats
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import numpy as np
import pathlib, json, glob, os
import random


counters = {
    "CPU_CLK_UNHALTED.REF_TSC":                                 "--event=00 --umask=03",
    "LD_BLOCKS.STORE_FORWARD":                                  "--event=03 --umask=02",
    "LD_BLOCKS.NO_SR":                                          "--event=03 --umask=08",
    "LD_BLOCKS_PARTIAL.ADDRESS_ALIAS":                          "--event=07 --umask=01",
    "DTLB_LOAD_MISSES.MISS_CAUSES_A_WALK":                      "--event=08 --umask=01",
    "DTLB_LOAD_MISSES.WALK_COMPLETED_4K":                       "--event=08 --umask=02",
    "DTLB_LOAD_MISSES.WALK_COMPLETED_2M_4M":                    "--event=08 --umask=04",
    "DTLB_LOAD_MISSES.WALK_COMPLETED_1G":                       "--event=08 --umask=08",
    "DTLB_LOAD_MISSES.WALK_COMPLETED":                          "--event=08 --umask=0E",
    "DTLB_LOAD_MISSES.WALK_PENDING":                            "--event=08 --umask=10",
    "DTLB_LOAD_MISSES.WALK_ACTIVE":                             "--event=08 --umask=10 --counter-mask=1",
    "DTLB_LOAD_MISSES.STLB_HIT":                                "--event=08 --umask=20",
    "INT_MISC.RECOVERY_CYCLES":                                 "--event=0D --umask=01",
    "INT_MISC.RECOVERY_CYCLES_ANY":                             "--event=0D --umask=01 --anyt", # Acidentially was umask=0D
    "INT_MISC.CLEAR_RESTEER_CYCLES":                            "--event=0D --umask=80",
    "UOPS_ISSUED.ANY":                                          "--event=0D --umask=80",
    "UOPS_ISSUED.STALL_CYCLES":                                 "--event=0E --umask=01 --counter-mask=1 --invert",
    "UOPS_ISSUED.VECTOR_WIDTH_MISMATCH":                        "--event=0E --umask=02",
    "UOPS_ISSUED.SLOW_LEA":                                     "--event=0E --umask=20",
    "ARITH.DIVIDER_ACTIVE":                                     "--event=14 --umask=01",
    "L2_RQSTS.DEMAND_DATA_RD_MISS":                             "--event=24 --umask=21",
    "L2_RQSTS.RFO_MISS":                                        "--event=24 --umask=22",
    "L2_RQSTS.CODE_RD_MISS":                                    "--event=24 --umask=24",
    "L2_RQSTS.ALL_DEMAND_MISS":                                 "--event=24 --umask=27",
    "L2_RQSTS.PF_MISS":                                         "--event=24 --umask=38",
    "L2_RQSTS.MISS":                                            "--event=24 --umask=3F",
    "L2_RQSTS.DEMAND_DATA_RD_HIT":                              "--event=24 --umask=41",
    "L2_RQSTS.RFO_HIT":                                         "--event=24 --umask=42",
    "L2_RQSTS.CODE_RD_HIT":                                     "--event=24 --umask=44",
    "L2_RQSTS.PF_HIT":                                          "--event=24 --umask=D8",
    "L2_RQSTS.ALL_DEMAND_DATA_RD":                              "--event=24 --umask=E1",
    "L2_RQSTS.ALL_RFO":                                         "--event=24 --umask=E2",
    "L2_RQSTS.ALL_CODE_RD":                                     "--event=24 --umask=E4",
    "L2_RQSTS.ALL_DEMAND_REFERENCES":                           "--event=24 --umask=E7",
    "L2_RQSTS.ALL_PF":                                          "--event=24 --umask=E8",
    "L2_RQSTS.REFERENCES":                                      "--event=24 --umask=FF",
    "CORE_POWER.LVL0_TURBO_LICENSE":                            "--event=28 --umask=07",
    "CORE_POWER.LVL1_TURBO_LICENSE":                            "--event=28 --umask=18",
    "CORE_POWER.LVL2_TURBO_LICENSE":                            "--event=28 --umask=20",
    "CORE_POWER.THROTTLE":                                      "--event=28 --umask=40",
    "LONGEST_LAT_CACHE.MISS":                                   "--event=2E --umask=41",
    "LONGEST_LAT_CACHE.REFERENCE":                              "--event=2E --umask=4F",
    "CPU_CLK_UNHALTED.THREAD_P":                                "--event=3C --umask=00",
    "CPU_CLK_UNHALTED.THREAD_P_ANY":                            "--event=3C --umask=00 --anyt",
    "CPU_CLK_UNHALTED.RING0_TRANS":                             "--event=3C --umask=00 --counter-mask=1 --edge-detect",
    "CPU_CLK_UNHALTED.REF_XCLK":                                "--event=3C --umask=01",
    "CPU_CLK_UNHALTED.REF_XCLK_ANY":                            "--event=3C --umask=01 --anyt",
    "CPU_CLK_UNHALTED.ONE_THREAD_ACTIVE":                       "--event=3C --umask=02",
    "L1D_PEND_MISS.PENDING":                                    "--event=48 --umask=01",
    "L1D_PEND_MISS.PENDING_CYCLES":                             "--event=48 --umask=01 --counter-mask=1",
    "L1D_PEND_MISS.PENDING_CYCLES_ANY":                         "--event=48 --umask=01 --counter-mask=1 --anyt",
    "L1D_PEND_MISS.FB_FULL":                                    "--event=48 --umask=02",
    "DTLB_STORE_MISSES.MISS_CAUSES_A_WALK":                     "--event=49 --umask=01",
    "DTLB_STORE_MISSES.WALK_COMPLETED_4K":                      "--event=49 --umask=02",
    "DTLB_STORE_MISSES.WALK_COMPLETED_2M_4M":                   "--event=49 --umask=04",
    "DTLB_STORE_MISSES.WALK_COMPLETED_1G":                      "--event=49 --umask=08",
    "DTLB_STORE_MISSES.WALK_COMPLETED":                         "--event=49 --umask=0e",
    "DTLB_STORE_MISSES.WALK_PENDING":                           "--event=49 --umask=10",
    "DTLB_STORE_MISSES.WALK_ACTIVE":                            "--event=49 --umask=10 --counter-mask=1",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=49 --umask=20",
    "LOAD_HIT_PRE.SW_PF":                                       "--event=4C --umask=01",
    "EPT.WALK_PENDING":                                         "--event=4F --umask=10",
    "L1D.REPLACEMENT":                                          "--event=51 --umask=01",
    "TX_MEM.ABORT_CONFLICT":                                    "--event=54 --umask=01",
    "TX_MEM.ABORT_CAPACITY":                                    "--event=54 --umask=02",
    "TX_MEM.ABORT_CAPACITY":                                    "--event=54 --umask=04",
    "TX_MEM.ABORT_HLE_ELISION_BUFFER_NOT_EMPTY":                "--event=54 --umask=08",
    "TX_MEM.ABORT_HLE_ELISION_BUFFER_MISMATCH":                 "--event=54 --umask=10",
    "TX_MEM.ABORT_HLE_ELISION_BUFFER_UNSUPPORTED_ALIGNMENT":    "--event=54 --umask=20",
    "TX_MEM.HLE_ELISION_BUFFER_FULL":                           "--event=54 --umask=40",
    "TX_EXEC.MISC1":                                            "--event=5D --umask=01",
    "TX_EXEC.MISC2":                                            "--event=5D --umask=02",
    "TX_EXEC.MISC3":                                            "--event=5D --umask=04",
    "TX_EXEC.MISC4":                                            "--event=5D --umask=08",
    "TX_EXEC.MISC5":                                            "--event=5D --umask=10",
    "RS_EVENTS.EMPTY_CYCLES":                                   "--event=5E --umask=01",
    "RS_EVENTS.EMPTY_END":                                      "--event=5E --umask=01 --counter-mask=1 --edge-detect --invert",
    "OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD":              "--event=60 --umask=01",
    "OFFCORE_REQUESTS_OUTSTANDING.CYCLES_WITH_DEMAND_DATA_RD":  "--event=60 --umask=01 --counter-mask=1",
    "OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD_GE_6":         "--event=60 --umask=01 --counter-mask=6",
    "OFFCORE_REQUESTS_OUTSTANDING.DEMAND_CODE_RD":              "--event=60 --umask=02 --counter-mask=1",
    "OFFCORE_REQUESTS_OUTSTANDING.DEMAND_RFO":                  "--event=60 --umask=04 --counter-mask=1",
    "OFFCORE_REQUESTS_OUTSTANDING.ALL_DATA_RD":                 "--event=60 --umask=08",
    "OFFCORE_REQUESTS_OUTSTANDING.CYCLES_WITH_DATA_RD":         "--event=60 --umask=08 --counter-mask=1",
    "OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD":      "--event=60 --umask=10",
    "OFFCORE_REQUESTS_OUTSTANDING.CYCLES_WITH_L3_MISS_DEMAND_DATA_RD": "--event=60 --umask=10 --counter-mask=1",
    "OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD_GE_6": "--event=60 --umask=10 --counter-mask=6",
    "IDQ.MITE_UOPS":                                            "--event=79 --umask=04",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=04 --counter-mask=1",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=08",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=08 --counter-mask=1",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=10",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=18 --counter-mask=4",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=18 --counter-mask=1",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=20",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=24 --counter-mask=4",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=24 --counter-mask=1",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=30 --counter-mask=1",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=30 --counter-mask=1 --edge-detect",
    "DTLB_STORE_MISSES.STLB_HIT":                               "--event=79 --umask=30",
    "ICACHE_16B.IFDATA_STALL":                                  "--event=80 --umask=04",
    "ICACHE_64B.IFTAG_HIT":                                     "--event=83 --umask=01",
    "ICACHE_64B.IFTAG_MISS":                                    "--event=83 --umask=02",
    "ICACHE_64B.IFTAG_STALL":                                   "--event=83 --umask=04",
    "ITLB_MISSES.MISS_CAUSES_A_WALK":                           "--event=85 --umask=01",
    "ITLB_MISSES.WALK_COMPLETED_4K":                            "--event=85 --umask=02",
    "ITLB_MISSES.WALK_COMPLETED_2M_4M":                         "--event=85 --umask=04",
    "ITLB_MISSES.WALK_COMPLETED_1G":                            "--event=85 --umask=08",
    "ITLB_MISSES.WALK_COMPLETED":                               "--event=85 --umask=0E",
    "ITLB_MISSES.WALK_PENDING":                                 "--event=85 --umask=10",
    "ITLB_MISSES.WALK_ACTIVE":                                  "--event=85 --umask=10 --counter-mask=1",
    "ITLB_MISSES.STLB_HIT":                                     "--event=85 --umask=20",
    "ILD_STALL.LCP":                                            "--event=87 --umask=01",
    "IDQ_UOPS_NOT_DELIVERED.CORE":                              "--event=9C --umask=01",
    "IDQ_UOPS_NOT_DELIVERED.CYCLES_0_UOPS_DELIV.CORE":          "--event=9C --umask=01 --counter-mask=4",
    "IDQ_UOPS_NOT_DELIVERED.CYCLES_LE_1_UOP_DELIV.CORE":        "--event=9C --umask=01 --counter-mask=3",
    "IDQ_UOPS_NOT_DELIVERED.CYCLES_LE_2_UOP_DELIV.CORE":        "--event=9C --umask=01 --counter-mask=2",
    "IDQ_UOPS_NOT_DELIVERED.CYCLES_LE_3_UOP_DELIV.CORE":        "--event=9C --umask=01 --counter-mask=1",
    "IDQ_UOPS_NOT_DELIVERED.CYCLES_FE_WAS_OK":                  "--event=9C --umask=01 --counter-mask=1 --invert",
    "UOPS_DISPATCHED_PORT.PORT_0":                              "--event=A1 --umask=01",
    "UOPS_DISPATCHED_PORT.PORT_1":                              "--event=A1 --umask=02",
    "UOPS_DISPATCHED_PORT.PORT_2":                              "--event=A1 --umask=04",
    "UOPS_DISPATCHED_PORT.PORT_3":                              "--event=A1 --umask=08",
    "UOPS_DISPATCHED_PORT.PORT_4":                              "--event=A1 --umask=10",
    "UOPS_DISPATCHED_PORT.PORT_5":                              "--event=A1 --umask=20",
    "UOPS_DISPATCHED_PORT.PORT_6":                              "--event=A1 --umask=40",
    "UOPS_DISPATCHED_PORT.PORT_7":                              "--event=A1 --umask=80",
    "RESOURCE_STALLS.ANY":                                      "--event=A2 --umask=01",
    "RESOURCE_STALLS.SB":                                       "--event=A2 --umask=08",
}

print("                                 counter     normal     slow")
for name, cmd in counters.items():
    p = Popen(["target/release/seismograph", "--stdout"] + cmd.split(' '), stdout=PIPE, stderr=PIPE)

    output = p.stdout.read()
    data = json.loads(output)

    times = [[], []]
    uops = [[], []]
    values = [[], []]
    for p in data["data"]:
        if p["uops_retired"] < 600:
            i = 0
        else:
            i = 1

        times[i].append(float(p["average_cycles"])/2.4 + random.random() - 0.5)
        uops[i].append(p["uops_retired"])
        values[i].append(p["counter"])

    if int(np.median(values[0])) == 0 and  int(np.median(values[1])) == 0:
        print("{}".format(name.rjust(50)))
    else:
        print("{}   {:>8} {:>8}".format(name.rjust(50), int(np.median(values[0])), int(np.median(values[1]))))
