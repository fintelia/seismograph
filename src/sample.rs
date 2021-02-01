use std::fs;

pub(crate) fn get_cpu_frequency() -> u32 {
    let freq = fs::read_to_string("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").unwrap();
    freq.trim().parse().unwrap()
}

pub(crate) fn start_timer() -> u64 {
    let cycles_low: u32;
    let cycles_high: u32;

    unsafe {
        asm!("cpuid; rdtsc",
            out("eax") cycles_low,
            out("ebx") _,
            out("ecx") _,
            out("edx") cycles_high,
        )
    }

    ((cycles_high as u64) << 32) | cycles_low as u64
}

pub(crate) fn stop_timer() -> u64 {
    let cycles_low: u32;
    let cycles_high: u32;

    unsafe {
        asm!("rdtscp; mov {cycles_low:e}, eax; mov {cycles_high:e}, edx; cpuid",
            cycles_low = out(reg) cycles_low,
            cycles_high = out(reg) cycles_high,
            out("eax") _,
            out("ebx") _,
            out("ecx") _,
            out("edx") _,
        )
    }

    ((cycles_high as u64) << 32) | cycles_low as u64
}

pub(crate) fn rdpmc(idx: u32) -> u64 {
    let value_low: u32;
    let value_high: u32;

    unsafe {
        asm!("rdpmc",
            out("eax") value_low,
            in("ecx") idx,
            out("edx") value_high,
        )
    }

    ((value_high as u64) << 32) | value_low as u64
}
