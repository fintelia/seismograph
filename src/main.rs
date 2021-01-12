use crate::run::Datapoint;
use chrono::{DateTime, Utc};
use indicatif::{ProgressBar, ProgressStyle};
use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    fs::{self, File},
    io::BufWriter,
    path::PathBuf,
    sync::atomic::{AtomicBool, Ordering},
};
use structopt::StructOpt;
use walkdir::WalkDir;

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
    profile: String,
    experiment_start: DateTime<Utc>,
    experiment_end: DateTime<Utc>,
    cpuinfo: String,
    source_code: HashMap<PathBuf, String>,
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
        profile: if cfg!(debug_assertions) {
            "debug"
        } else {
            "release"
        }
        .to_string(),
        experiment_start: Utc::now(),
        experiment_end: Utc::now(), // will be overwritten once the experiment ends
        source_code: HashMap::new(),
        data: Vec::new(),
    };

    for entry in WalkDir::new(format!("{}/src", env!("CARGO_MANIFEST_DIR")))
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
    {
        trace.source_code.insert(
            entry.path().to_owned(),
            fs::read_to_string(entry.path()).unwrap(),
        );
    }

    while trace.data.len() < MAX_DATAPOINTS && !EXIT.load(Ordering::SeqCst) {
        trace.data.push(run::single_iter());
        progress.set_position(trace.data.len() as u64);
        progress.set_length(progress.position() * 10000 / (1 + progress.position() % 10000));
    }
    trace.experiment_end = Utc::now();
    progress.finish_at_current_pos();

    let writer = BufWriter::new(File::create(opt.output).unwrap());
    serde_json::to_writer_pretty(writer, &trace).unwrap();
}
