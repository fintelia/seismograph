use crate::sample;
use perfcnt::linux::{PerfCounter, PerfCounterBuilderLinux, MMAPPage};
use perfcnt::AbstractPerfCounter;
use serde::{Deserialize, Serialize};
use std::convert::TryInto;
use x86::perfcnt::intel::{EventDescription, Tuple, Counter, MSRIndex, PebsType};
use std::mem;

#[derive(Serialize, Deserialize)]
pub(crate) struct Datapoint {
    pub cpu_frequency: u32,
    pub average_cycles: u32,
	pub counter: u32,
	pub enabled_cycles: u32,
}

const ITERATIONS: usize = 1;

pub(crate) fn single_iter() -> Datapoint {
    let mut builder = PerfCounterBuilderLinux::from_intel_event_description(&EventDescription {
		event_code: Tuple::One(0x0e),
		umask: Tuple::One(0x01),
		counter_mask: 0x0,
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
    });
    builder.pinned();
    builder.enable_read_format_time_enabled();
    //builder.enable_read_format_time_running();
    let mut pc: PerfCounter = builder.finish().unwrap();

    let mmap = pc.mmap_header();
    let pc_header = unsafe { mem::transmute::<*mut u8, &mut MMAPPage>(mmap.data()) };

    assert_eq!(pc_header.capabilities, 0x1e);

	let idx = pc_header.index - 1;

    pc.start().unwrap();
    let start = sample::start_timer();
    let counter_start = sample::rdpmc(idx);

    for _ in 0..ITERATIONS {
        unsafe { libc::syscall(libc::SYS_getpid) };
    }

    let counter_elapsed = sample::rdpmc(idx) - counter_start;
    let elapsed = sample::stop_timer() - start;
    pc.stop().unwrap();

    let average_cycles = elapsed as u32 / ITERATIONS as u32;
    let cpu_frequency = sample::get_cpu_frequency();

    let counter_full = pc.read_fd().unwrap();

    Datapoint {
        average_cycles,
        cpu_frequency,
		counter: counter_elapsed as u32,// counter_full.value.try_into().unwrap(),
		enabled_cycles: counter_full.time_enabled.try_into().unwrap(),
    }
}
