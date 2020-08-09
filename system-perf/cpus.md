# CPUs

## Terminology

- Processor: physical chip with 1+ CPUs implemented as cores or hardware threads
- Core: independent CPU instance on a multi-core processor (multiprocessing)
- Hardware thread: supports executing multiple threads in parallel on a single core where each thread is an independent CPU instance (multithreading)
- CPU instruction: single CPU operation
- Logical CPU: virtual processor
- Scheduler: kernel subsystem that assigns threads to run on CPUs
- Run queue: queue of runnable threads waiting to be serviced by CPUs

## Concepts

- Clock Rate
    * Digital signal that drives all processor logic
    * CPU instruction takes one or more cycles (CPU cycles) to execute
    * CPUs execute at a clock rate e.g., 5GHz performs 5 billion clock cycles per second
- Instruction
    * Instruction includes:
        1. Instruction fetch
        2. Instruction decode
        3. Execute
        4. Memory access
        5. Register write-back
    * Each step takes at least one clock cycle
    * Memory can take dozens of clock cycles (CPU caching important)
- Cycles per instruction: high-level metric for describing where a CPU is spending its clock cycles and understanding nature of CPU utilization
    * High CPI indicates CPUs are often stalled typically for memory access
- CPU utilization: time CPU is busy performing work during an interval (%)
    * Performance does not degrade steeply with high utilization
    * Kernel prioritizes processes
- Saturation: CPU at 100% utilization
    * Threads encounter scheduler latency as they wait for on-cpu time
- Preemption: allows higher-priority thread to preempt running thread to beign its own execution
    * Elimiates run-queue latency for higher-priority work
- Multiprocess
    * Use `fork()`
    * Separate address space per process
    * Cost of `fork()`, `exit()`
    * Communicate with IPC which incurs CPU cost; context switching to move data between address spaces
- Multithreading
    * Use `threads` API
    * Small memory overhead
    * Small CPU overhead; just API calls
    * Direct access to share memory (integrity via synchroonization primitives)
- Word size
    * Processors designed around a max word size e.g., 32-bit or 64-bit which is the integer size and register size.
- CPU performance couonters
    * Counters for:
        1. CPU cycles
        2. CPU instructions
        3. Level 1,2,3 cache access (miss and hits)
        4. Floating point unit
        5. Memory I/O
        6. Resource I/O