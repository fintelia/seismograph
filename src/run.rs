use crate::sample;
use perfcnt::linux::{PerfCounter, PerfCounterBuilderLinux, MMAPPage};
use perfcnt::AbstractPerfCounter;
use serde::{Deserialize, Serialize};
use x86::perfcnt::intel::{EventDescription, Tuple, Counter, MSRIndex, PebsType};
use std::mem;

#[derive(Serialize, Deserialize)]
pub(crate) struct Datapoint {
    pub average_cycles: u32,
	pub counter: u32,
	pub counter2: u32,
}

const ITERATIONS: usize = 1;

pub(crate) struct Experiment {
	_pc: PerfCounter,
	mmap: mmap::MemoryMap,
	_pc2: PerfCounter,
	mmap2: mmap::MemoryMap,
}
impl Experiment {
	pub fn new(opt: &super::Opt) -> Self {
		let event_desc = EventDescription {
			event_code: Tuple::One(0x0e),
			umask: Tuple::One(0x01),
			counter_mask: 0,
			any_thread: false,
			edge_detect: false,
			invert: false,

			// unused
			event_name: "",
			brief_description: "",
			public_description: None,
			counter: Counter::Fixed(0),
			counter_ht_off: None,
			pebs_counters: None,
			sample_after_value: 0,
			msr_index: MSRIndex::None,
			msr_value: 0,
			precise_store: false,
			collect_pebs_record: None,
			data_la: false,
			l1_hit_indication: false,
			errata: None,
			offcore: false,
			unit: None,
			filter: None,
			extsel: false,
			uncore: false,
			deprecated: false,
			event_status: 0,
			fc_mask: 0,
			filter_value: 0,
			port_mask: 0,
			umask_ext: 0,
			pebs: PebsType::Regular,
			taken_alone: false,
		};
		let mut builder = PerfCounterBuilderLinux::from_intel_event_description(&event_desc);
		builder.pinned();
		//builder.enable_read_format_time_enabled();
		//builder.enable_read_format_time_running();
		let pc: PerfCounter = builder.finish().unwrap();
		let mmap = pc.mmap_header();
		pc.start().unwrap();

		let mut builder2 = PerfCounterBuilderLinux::from_intel_event_description(&EventDescription {
			event_code: Tuple::One(opt.event), // 0x0e
			umask: Tuple::One(opt.umask), // 0x01
			counter_mask: opt.counter_mask, // 0
			any_thread: opt.anyt,
			edge_detect: opt.edge_detect,
			invert: opt.invert,
			..event_desc
		});
		builder2.pinned();
		//builder.enable_read_format_time_enabled();
		//builder.enable_read_format_time_running();
		let pc2: PerfCounter = builder2.finish().unwrap();
		let mmap2 = pc2.mmap_header();
		pc2.start().unwrap();


		Self {
			_pc: pc,
			mmap,
			_pc2: pc2,
			mmap2,
		}
	}

	pub fn single_iter(&mut self) -> Datapoint {
		let pc_header = unsafe { mem::transmute::<*mut u8, &mut MMAPPage>(self.mmap.data()) };
		let idx = pc_header.index - 1;

		let pc_header2 = unsafe { mem::transmute::<*mut u8, &mut MMAPPage>(self.mmap2.data()) };
		let idx2 = pc_header2.index - 1;

		let start = sample::start_timer();
		let counter_start = sample::rdpmc(idx);
		let counter2_start = sample::rdpmc(idx2);

		for _ in 0..ITERATIONS {
			unsafe { libc::syscall(libc::SYS_getpid) };
			// std::hint::black_box(f64::sqrt(std::hint::black_box(12345.0)));
		}

		let counter2_elapsed = sample::rdpmc(idx2) - counter2_start;
		let counter_elapsed = sample::rdpmc(idx) - counter_start;
		let elapsed = sample::stop_timer() - start;

		let average_cycles = elapsed as u32 / ITERATIONS as u32;
		// let cpu_frequency = sample::get_cpu_frequency();

		Datapoint {
			average_cycles,
			counter: counter_elapsed as u32,
			counter2: counter2_elapsed as u32,
		}
	}
}
