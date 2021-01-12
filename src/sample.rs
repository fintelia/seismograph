use std::fs;

pub(crate) fn get_cpu_frequency() -> u32 {
    let freq = fs::read_to_string("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").unwrap();
    freq.trim().parse().unwrap()
}

