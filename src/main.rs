use indicatif::{ProgressBar, ProgressStyle};
use serde::{Deserialize, Serialize};
use std::{
    fs::{self, File},
    io::BufWriter,
    path::PathBuf,
    sync::atomic::{AtomicBool, Ordering},
    time::Instant,
};
use structopt::StructOpt;

const MAX_DATAPOINTS: usize = 10_000_000;

static EXIT: AtomicBool = AtomicBool::new(false);

#[derive(Debug, StructOpt)]
struct Opt {
    #[structopt(short, long, default_value = "trace.json")]
    output: PathBuf,
}

#[derive(Serialize, Deserialize, Debug, Default)]
struct Datapoint {
    elapsed_seconds: f32,
    cpu_frequency: u32,
}

#[derive(Serialize, Deserialize)]
struct TraceFile {
    hostname: String,
    kernel: String,
    cmdline: String,
    cpuinfo: String,
    data: Vec<Datapoint>,
}

fn get_cpu_frequency() -> u32 {
    let freq = fs::read_to_string("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").unwrap();
    freq.trim().parse().unwrap()
}

fn main() {
    ctrlc::set_handler(move || {
        if EXIT.load(Ordering::SeqCst) {
            unsafe {
                libc::exit(1);
            }
        }
        EXIT.store(true, Ordering::SeqCst);
    })
    .unwrap();

    let opt = Opt::from_args();

    let progress = ProgressBar::new(MAX_DATAPOINTS as u64);
    progress.set_style(
        ProgressStyle::default_bar()
            .template("[{elapsed_precise}] {bar:40.cyan/blue} {pos}")
            .progress_chars("##-"),
    );

    let mut trace = TraceFile {
        hostname: fs::read_to_string("/proc/sys/kernel/hostname").unwrap(),
        kernel: fs::read_to_string("/proc/version").unwrap(),
        cmdline: fs::read_to_string("/proc/cmdline").unwrap(),
        cpuinfo: fs::read_to_string("/proc/cpuinfo").unwrap(),
        data: Vec::new(),
    };

    while trace.data.len() < MAX_DATAPOINTS && !EXIT.load(Ordering::SeqCst) {
        let start = Instant::now();
        for _ in 0..10000 {
            unsafe { libc::syscall(libc::SYS_getpid) };
        }

        let elapsed_seconds = start.elapsed().as_secs_f32();
        let cpu_frequency = get_cpu_frequency(); 

        trace.data.push(Datapoint {
            elapsed_seconds,
            cpu_frequency,
        });
        progress.set_position(trace.data.len() as u64);
        progress.set_length(progress.position() * 10000 / (1 + progress.position() % 10000));
    }
    progress.finish_at_current_pos();

    let t = Instant::now();

    let writer = BufWriter::new(File::create(opt.output).unwrap());
    serde_json::to_writer_pretty(writer, &trace).unwrap();

    println!("{} ns/datapoint", t.elapsed().as_nanos() as f64 / trace.data.len() as f64);
}
