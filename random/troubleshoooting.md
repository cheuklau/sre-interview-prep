# Troubleshoooting

## Effective Troubleshooting (Soure: Google SRE - Chapter 13)

- Steps:
    1. Problem report
        * What is the expected behavior?
        * What is the actual behavior?
        * How to reproduce the behavior?
    2. Triage
        * How to make system work as well as possible?
    3. Examine
        * USE method (next section)
        * Examine each component's behavior.
        * Use system metrics.
        * Use logging, trace requests through the stack.
        * Expose RPC/API endpoints recently sent/received to understand how servers communicate.
    4. Diagnose
        * Develop plausible hypotheses.
        * Look at connections between componenets.
        * Ask what is malfunctioning system doing, why is it doing it, and where are its resouorces being used.
        * Find what touched it last e.g., new version deployed or configuration change.
    5. Test/treat
    6. Cure
- To troubleshoot easier:
    * Build observability.
    * Design well-understood and observable interfaces between components.
- Four golden signals:
    1. Latency: time to service a request
    2. Traffic: demand on system
    3. Errors: explicit (500), implicity (200 with wrong content), policy (slow 200s)
    4. Saturation: how full system is

## The USE Method (Source: http://www.brendangregg.com/usemethod.html)

- For every resource check:
    * Utilization
        + Average time resource was busy servicing work.
        + As percent over time e.g., Disk running at 90% utilization.
    * Saturation
        + Degree to which resource has extra work it can't service.
        + As a queue length e.g., CPUs have an average run queue of four.
    * Errors
        + Count of error events.
        + Scalar counts e.g., network interface had 50 late collisions.
- Notes:
    * Low utilization does not mean no saturation e.g., short bursts.
- Resources:
    * CPUs - sockets, cores, threads
        + Utilization: CPU utilization per-CPU or system-wide average
        + Saturation: run-queue length or scheduler latency
            * `vmstat 1` to run `vmstat` every second
            ```
            procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
            r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
            0  0      0 462720   2088 466352    0    0     1     5   15   31  0  0 100  0  0
            ```
    * Memory - capacity
        + Utilization: available free memory (system-wide)
        + Saturation: anonymous paging or thread swapping
    * Network interfaces
        + Utilization: RX/TX throughput, max bandwidth
    * Storage devices - I/O, capacity
        + Utilization: Device busy percent
        + Saturation: Wait queue length
        + Errors: Device errors
    * Controllers - storage, network cards
    * Interconnects - CPUs, memory, I/O
- Some physical components left out e.g., caches which improve performance under high utilization.