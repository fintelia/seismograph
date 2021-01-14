use std::time::Instant;
use serde::{Deserialize, Serialize};
use crate::sample;

#[derive(Serialize, Deserialize)]
pub(crate) struct Datapoint {
    pub average_time: f32,
    pub cpu_frequency: u32,
}

pub(crate) fn single_iter() -> Datapoint {
    let start = Instant::now();

    for _ in 0..100000 {
        unsafe { libc::syscall(libc::SYS_getpid) };
    }

    let average_time = start.elapsed().as_secs_f32() / 100000.0;
    let cpu_frequency = sample::get_cpu_frequency(); 

    Datapoint {
        average_time,
        cpu_frequency,
    }
}