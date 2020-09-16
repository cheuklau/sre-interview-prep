# Application

## Methoodology and Analysis

### Thread State Analysis

- Where application threads are spending their time
- Two states:
    * On-CPU: executing
    * Off-CPU: waiting for turn, I/O, locks, paging, etc
- Six states
    * Executing
        + Check reason for CPU consumption via profiling
        + `top` reports this as `%CPU`
    * Runnable
        + App needs more CPU resources
        + `schedstats` via `/proc/<pid>/schedstat`
    * Anonymous paging
        + Lack of available main memory
        + Kernel delay accounting feature or tracing
    * Sleeping
        + Where is the app blocked (syscall analysis, I/O profiling)
        + `pidstat -d`, `iotop`, tracing
    * Lock
        + Identify lock, thread holding it and why held for so long
        + Tracing
    * Idle
- Want to minimize time spent in first five states (maximize idle)

### CPU Profiling

- Why is an app consuming CPU resources
- Sample on-CPU user-level stack trace and coalesce results
    * Visualize using flame graphs

### Syscall Analysis

- Executing: on-CPU (user mode)
- Syscalls: system call (kernel mode running or waiting)
    * I/O, locks, other syscall types
- For runnable and anonymous paging, check CPU and memory saturation via USE
- Executing state can be studied via CPU profiling
- `strace` to show system calls made, their return codes and time spent
    * Note: high overhead
    * Buffered tracing buffers instructumentation data in-kernel so target program can continue to execute
    * Differs from breakpoint tracig which interrupts target program for each tracepoint

### I/O Profiling

- Determines why and how I/O-related system alls are being performed
- Tracing filtering for read system calls for example

### USE Method

- Utilization, saturation and error of all hardware resources
- For software resuorces, depends on the app at hand
    * Example: app uses poool of woorker threads with a queue for requests to wait their turn
        + Utilization: average number of threads busy processing requests during an interval
        + Saturation: average length of request queue during an interval
        + Errors: requests denied or failed
    * Example: file descriptors
        + Utilization: % file descriptoors opened
        + Saturation: if threads block waiting for FD allocation
        + Errors: allocation errors

### Lock Analysis

- Check for excessive hold times
- CPU profiling shows spin locks, mutex locks

### Static Performance Tuning

- Latest version?
- Known performance issues?
- Configured correctly?
- Cache?
- App run concurrently?
- System libraries?
- Large heap pages?
- System imposed resource limits?