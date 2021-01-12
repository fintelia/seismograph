use indicatif::{ProgressBar, ProgressStyle};
use serde::{Deserialize, Serialize};
use std::{
    fs::{self, File},
    io::BufWriter,
    path::PathBuf,
    sync::atomic::{AtomicBool, Ordering},
};
use structopt::StructOpt;
use crate::run::Datapoint;

mod run;
mod sample;

const MAX_DATAPOINTS: usize = 10_000_000;
static EXIT: AtomicBool = AtomicBool::new(false);

#[derive(Debug, StructOpt)]
struct Opt {
    #[structopt(short, long, default_value = "trace.json")]
    output: PathBuf,
}

#[derive(Serialize, Deserialize)]
struct TraceFile {
    hostname: String,
    kernel: String,
    cmdline: String,
    cpuinfo: String,
    data: Vec<Datapoint>,
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
        trace.data.push(run::single_iter());
        progress.set_position(trace.data.len() as u64);
        progress.set_length(progress.position() * 10000 / (1 + progress.position() % 10000));
    }
    progress.finish_at_current_pos();

    let writer = BufWriter::new(File::create(opt.output).unwrap());
    serde_json::to_writer_pretty(writer, &trace).unwrap();
}
