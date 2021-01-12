use std::time::Instant;
use serde::{Deserialize, Serialize};
use crate::sample;

#[derive(Serialize, Deserialize)]
pub(crate) struct Datapoint {
    elapsed_seconds: f32,
    cpu_frequency: u32,
}

pub(crate) fn single_iter() -> Datapoint {
    let start = Instant::now();
    
    for _ in 0..10000 {
        unsafe { libc::syscall(libc::SYS_getpid) };
    }

    let elapsed_seconds = start.elapsed().as_secs_f32();
    let cpu_frequency = sample::get_cpu_frequency(); 

    Datapoint {
        elapsed_seconds,
        cpu_frequency,
    }
}