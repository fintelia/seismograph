#![feature(asm)]
#![feature(test)]

use crate::run::Datapoint;
use chrono::{DateTime, SecondsFormat, Utc};
use indicatif::{ProgressBar, ProgressStyle};
use serde::{Deserialize, Serialize};
use sha2::Digest;
use std::{collections::HashMap, fs::{self, File}, io::BufWriter, num::ParseIntError, path::PathBuf, sync::atomic::{AtomicBool, Ordering}};
use structopt::StructOpt;
use walkdir::WalkDir;

mod run;
mod sample;

include!(concat!(env!("OUT_DIR"), "/source_hashes.rs"));

const MAX_DATAPOINTS: usize = 500_000;
static EXIT: AtomicBool = AtomicBool::new(false);

fn parse_hex(src: &str) -> Result<u8, ParseIntError> {
    u8::from_str_radix(src, 16)
}

#[derive(Debug, StructOpt)]
struct Opt {
    #[structopt(short, long, default_value = "trace.json")]
    output_suffix: String,
    #[structopt(long, parse(try_from_str = parse_hex))]
    event: u8,
    #[structopt(long, parse(try_from_str = parse_hex))]
    umask: u8,
    #[structopt(long, default_value = "0")]
    counter_mask: u8,
    #[structopt(long)]
    invert: bool,
    #[structopt(long)]
    edge_detect: bool,
    #[structopt(long)]
    anyt: bool,
    #[structopt(long)]
    stdout: bool,
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
        let source = fs::read(entry.path()).unwrap();
        let hash = hex::encode(sha2::Sha256::digest(&source).as_slice());
        let source_matches = SOURCE_HASHES
            .get(&*entry.path().to_string_lossy())
            .map(|h| *h == &hash)
            .unwrap_or(false);

        if !source_matches {
            eprintln!("ERROR: source file '{}' changed", entry.path().display());
            return;
        }

        trace
            .source_code
            .insert(entry.into_path(), String::from_utf8_lossy(&source).into());
    }

    let opt = Opt::from_args();
    let trace_file_path = format!(
        "trace/{}-{}",
        trace
            .experiment_start
            .to_rfc3339_opts(SecondsFormat::Secs, true)
            .replace(':', "."),
        opt.output_suffix
    );
    eprintln!("Recording '{}'...", trace_file_path);

    let mask = 0x4u128;
    unsafe { libc::sched_setaffinity(0, 16, &mask as *const u128 as *const _); }

    let progress = ProgressBar::new(MAX_DATAPOINTS as u64);
    progress.set_style(
        ProgressStyle::default_bar()
            .template("[{elapsed_precise}] {bar:40.cyan/blue} {pos}")
            .progress_chars("##-"),
    );
    progress.set_draw_delta(1000);
    let mut experiment = run::Experiment::new(&opt);
    while trace.data.len() < MAX_DATAPOINTS && !EXIT.load(Ordering::SeqCst) {
        trace.data.push(experiment.single_iter());
        progress.set_position(trace.data.len() as u64);
        progress.set_length(progress.position() * 100000 / (1 + progress.position() % 100000));
    }
    trace.experiment_end = Utc::now();
    progress.finish_at_current_pos();

    if opt.stdout {
        let stdout = std::io::stdout();
        let handle = stdout.lock();
        serde_json::to_writer_pretty(handle, &trace).unwrap();
    } else {
        fs::create_dir_all("trace").unwrap();
        let writer = BufWriter::new(File::create(trace_file_path).unwrap());
        serde_json::to_writer_pretty(writer, &trace).unwrap();
    }
}
