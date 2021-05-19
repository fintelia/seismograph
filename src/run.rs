use crate::sample;
use perfcnt::linux::{PerfCounter, PerfCounterBuilderLinux, MMAPPage, SamplingPerfCounter, Event, HardwareEventType};
use perfcnt::AbstractPerfCounter;
use serde::{Deserialize, Serialize};
use x86::perfcnt::intel::{EventDescription, Tuple, Counter, MSRIndex, PebsType};
use std::mem;

#[derive(Serialize, Deserialize)]
pub(crate) struct Datapoint {
    pub average_cycles: u64,
	pub uops_retired: u64,
	pub counter: u64,
	// pub kernel_ip: u64,
	// pub dt: i64,
}

const ITERATIONS: usize = 1;

#[inline(never)]
fn do_nop() {}

pub(crate) struct Experiment {
	_pc: PerfCounter,
	mmap: mmap::MemoryMap,
	_pc2: PerfCounter,
	mmap2: mmap::MemoryMap,
	// sampling_pc: SamplingPerfCounter,

    // time_shift: u16,
    // time_mult: u32,
    // time_offset: u64,
	// time_zero: u64,

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

		let (pc, mmap) = {
			let mut builder = PerfCounterBuilderLinux::from_intel_event_description(&event_desc);
			builder.pinned();
			let pc: PerfCounter = builder.finish().unwrap();
			let mmap = pc.mmap_header();
			pc.start().unwrap();
			(pc, mmap)
		};

		let (pc2, mmap2) = {
			let mut builder = PerfCounterBuilderLinux::from_intel_event_description(&EventDescription {
				event_code: Tuple::One(opt.event), // 0x0e
				umask: Tuple::One(opt.umask), // 0x01
				counter_mask: opt.counter_mask, // 0
				any_thread: opt.anyt,
				edge_detect: opt.edge_detect,
				invert: opt.invert,

				msr_index: MSRIndex::None,
				pebs: PebsType::Regular,
				..event_desc
			});
			builder.pinned();
			let pc: PerfCounter = builder.finish().unwrap();
			let mmap = pc.mmap_header();
			pc.start().unwrap();
			(pc, mmap)
		};

		// let sampling_pc = {
		// 	let mut builder = PerfCounterBuilderLinux::from_hardware_event(HardwareEventType::CPUCycles);
 		// 	builder.pinned();
		// 	builder.enable_sampling_ip();
		// 	// builder.enable_read_format_id();
		// 	// builder.enable_read_format_time_enabled();
		// 	// builder.enable_read_format_time_running();
		// 	builder.enable_sampling_time();
		// 	builder.enable_sampling_identifier();
		// 	builder.enable_sampling_tid();
		// 	builder.set_sample_period(10000);
		// 	builder.exclude_user();
		// 	SamplingPerfCounter::new(builder.finish().unwrap())
		// };

		// dbg!(sampling_pc.header().capabilities);

		Self {
			_pc: pc,
			mmap,
			_pc2: pc2,
			mmap2,
			// time_shift: dbg!(sampling_pc.header().time_shift),
			// time_mult: dbg!(sampling_pc.header().time_mult),
			// time_offset: dbg!(sampling_pc.header().time_offset),
			// time_zero: dbg!(sampling_pc.header().time_zero),
			// sampling_pc,
		}
	}

	pub fn single_iter(&mut self, iter_number: usize) -> Datapoint {
		let pc_header = unsafe { mem::transmute::<*mut u8, &mut MMAPPage>(self.mmap.data()) };
		let idx = pc_header.index - 1;

		let pc_header2 = unsafe { mem::transmute::<*mut u8, &mut MMAPPage>(self.mmap2.data()) };
		let idx2 = pc_header2.index - 1;

		let counter_start = sample::rdpmc(idx);
		let counter2_start = sample::rdpmc(idx2);
		let start = sample::start_timer();

		let mut low0: u32 = 0;
		let mut low1: u32 = 0;
		let mut high0: u32 = 0;
		let mut high1: u32 = 0;
		for _ in 0..ITERATIONS {
			if iter_number < 50000 {

			}
			else {
				unsafe {
					asm!("lfence; call r11", in("r11") do_nop);
				
	// 				asm!("
	// call __x86_indirect_thunk_r11;
	// jmp 5f;
	// __x86_indirect_thunk_r11:
	// 	call 4f;
	// 3:	pause;
	// 	lfence;
	// 	jmp 3b;
	// .align 16
	// 4:	mov [rsp], r11;
	// ret;
	// 5:",
	// 				in("r11") do_nop);
				}
			}
		}

		let end = sample::stop_timer();
		let counter2_elapsed = sample::rdpmc(idx2) - counter2_start;
		let counter_elapsed = sample::rdpmc(idx) - counter_start;
		let elapsed = end - start;

		let average_cycles = elapsed / ITERATIONS as u64;
		// let cpu_frequency = sample::get_cpu_frequency();


		//let average_cycles = (((high1 as u64) << 32) | low1 as u64) - (((high0 as u64) << 32) | low0 as u64);

		// let mut kernel_ip = 0;
		// for event in &mut self.sampling_pc {
		// 	if let Event::Sample(ref record) = event {
		// 		let time = record.time - self.time_zero;
		// 		let quot = time / self.time_mult as u64;
		// 		let rem = time % self.time_mult as u64;
		// 		let timestamp = (quot << self.time_shift) + (rem << self.time_shift) / self.time_mult as u64;

		// 		if timestamp >= start && timestamp < end {
		// 			kernel_ip = record.ip;
		// 		}
		// 	}
		// }

		Datapoint {
			average_cycles: average_cycles,
			uops_retired: counter_elapsed,
			counter: counter2_elapsed,
			// kernel_ip,
		}
	}
}
