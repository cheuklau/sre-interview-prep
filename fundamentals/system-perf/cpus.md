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
- CPU performance counters
    * Counters for:
        1. CPU cycles
        2. CPU instructions
        3. Level 1,2,3 cache access (miss and hits)
        4. Floating point unit
        5. Memory I/O
        6. Resource I/O

## Methodology and Analysis

### Tools Method

- `uptime`: load averages over time
- `vmstat`: check idle columns to see how much headroom there is (<10% can be a problem)
- `mpstat`: check for hot CPUs to identify thread scability problem
- `top`: see which processes are top CPU consumers
- `pidstat`: break down top CPU consumers into user and system time
- `perf/dtrace`: profile CPU usage stack traces to identify why CPUs are in use

### USE Method

- Identify bottlenecks and errors across all components
- For CPU:
    * Utilization: time CPU was busy
        + Percent busy, check per CPU to see if there are scalability issues
    * Saturation: degree to which runnable threads are queued waiting for turn on CPU
    * Errors: CPU errors
        + Are all CPUs still online

### Workload Characterization

- Important for capacity planning, benchmarking and simulating workloads
- Skip since we care about troubleshooting

### Profiling

- Sampling the state of the CPU at timed intervals:
    1. Select type of proofile data to capture and rate
    2. Begin sampling at timed intervals
    3. Wait while activity of interest occurs
    4. End sampling and collect sample data
    5. Process the data
- Generate flame graphs
- CPU profile data on:
    * User and/or kernel level
    * Function and offset, function only, partial stack trace or full stack trace
- Sampling stack trace points to higher-level reasons for CPU usage

### Cycle Analysis

- For usage of specific CPU resources such as caches and interconnects, profiling can use CPU performance counters (CPC)-based event triggers instead of timed intervals
- Can reveal that cycles are spent stalled on Level 1, 2 or 3 cache misses, memory I/O or resuorce I/O or spent on floating-point operations or other activities

### Performance Monitoring

- Identify issues and patterns over time
- Key metrics for CPUs:
    1. Utilization: percent busy
    2. Saturation: run-queue length

### Static performance Tuning

- Examine:
    * CPUs available
    * Size of CPU caches
    * CPU clock speed
    * CPU-related features enabled/disabled by BIOS?
    * Software imposted CPU usage limits?

### Priority Tuning

- `nice` for adjusting process priority
- Identify low-priority work e.g., monitoring agents and scheduled backups and moofidy them to start with a higher `nice` value
- Can also change scheduler class/policy
- Real-time scheduling class allow processes to preempt all other work

### Resource Control

- Skip

### CPU Binding

- Bind processes and threads to individual CPUs or collection or CPUs
- Improve CPU cache warmth for processes, improving memory I/O performance

### Microbenchmarking

- Skip

### Scaling

- Skip

## Analysis

