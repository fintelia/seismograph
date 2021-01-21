use crate::sample;
use perfcnt::linux::{PerfCounter, PerfCounterBuilderLinux};
use perfcnt::AbstractPerfCounter;
use serde::{Deserialize, Serialize};
use std::convert::TryInto;

#[derive(Serialize, Deserialize)]
pub(crate) struct Datapoint {
    pub average_cycles: u32,
    pub cpu_frequency: u32,
    pub counter: u32,
}

const ITERATIONS: usize = 1;



pub(crate) fn single_iter() -> Datapoint {
    let mut builder = PerfCounterBuilderLinux::from_hardware_event(perfcnt::linux::HardwareEventType::CacheMisses);
    builder.pinned();
    let mut pc: PerfCounter = builder.finish().unwrap();

    pc.start().unwrap();
    let start = sample::start_timer();

    for _ in 0..ITERATIONS {
        unsafe { libc::syscall(libc::SYS_getpid) };
    }

    let elapsed = sample::stop_timer() - start;
    pc.stop().unwrap();

    let average_cycles = elapsed as u32 / ITERATIONS as u32;
    let cpu_frequency = sample::get_cpu_frequency();

    let counter = pc.read().unwrap().try_into().unwrap();

    Datapoint {
        average_cycles,
        cpu_frequency,
        counter,
    }
}
