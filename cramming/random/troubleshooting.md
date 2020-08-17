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
            - System-wide:
                * `vmstat 1`
                    ```
                    procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
                    r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
                    0  0      0 462720   2088 466352    0    0     1     5   15   31  0  0 100  0  0
                    ```
                    + Sum:
                        - `us`: time spent running non-kernel code
                        - `sy`: time spent running kernel code
                        - `st`: time stolen from VM
                * `sar -u`
                    ```
                    12:00:01 AM     CPU     %user     %nice   %system   %iowait    %steal     %idle
                    12:10:01 AM     all      0.02      0.00      0.01      0.00      0.02     99.95
                    ```
                    + Sum:
                        - `%user`: user level
                        - `%nice`: user level with nice priority
                        - `%system` kernel level
                        - `%steal`: involuntary wait while hypervisor servicing another virtual processor
                * `uptime` (Netflix Blog)
                    ```
                    05:22:33 up 3 days,  6:25,  1 user,  load average: 0.00, 0.00, 0.00
                    ```
                    + Shows three load average (1, 5, 15 minute averages)
            - Per-CPU:
                * `mpstat -P ALL 1`
                    ```
                    07:12:41 AM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
                    07:12:42 AM  all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
                    07:12:42 AM    0    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
                    ```
                    + Sum:
                        - `%usr`: user level
                        - `%nice`: user level with nice priority
                        - `%sys`: kernel level
                        - `%irq`: service hardware interrupts
                        - `%soft`: service software interrupts
                        - `%steal`: involuntary wait while hypervisor servicing anoother virtual processor
                        - `%guest`: run a virtual processor
                        - `%gnice`: run a niced guest
                * `sar -P ALL`
                    ```
                    07:00:02 AM     CPU     %user     %nice   %system   %iowait    %steal     %idle
                    07:10:01 AM     all      0.06      0.00      0.03      0.01      0.20     99.70
                    07:10:01 AM       0      0.06      0.00      0.03      0.01      0.20     99.70
                    ```
                    + Sum:
                        - `%user`
                        - `%nice`
                        - `%system`
                        - `%steal`
            - Per-process:
                * `top`
                    ```
                    PID USER  PR NI   VIRT  RES  SHR S %CPU %MEM   TIME+ COMMAND
                    1   rooot 20  0 125560 5416 3928 S  0.0  0.5 0:05.61 systemd
                    ```
                    + `%CPU`
                * `pidstat 1`
                    ```
                    07:26:44 AM   UID       PID    %usr %system  %guest    %CPU   CPU  Command
                    07:26:45 AM  1000     14844    1.00    0.00    0.00    1.00     0  pidstat
                    ```
                    + `%CPU`
            - Per-kernel-thread:
                * `top` with `K` toggle
        + Saturation: run-queue length or scheduler latency
            - System-wide
                * `vmstat 1` to run `vmstat` every second
                    ```
                    procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
                    r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
                    0  0      0 462720   2088 466352    0    0     1     5   15   31  0  0 100  0  0
                    ```
                    + Check for `r` > CPU count where `r` is the number of processes waiting for run time
                    + Note: can get CPU count with `lscpu`
                * `sar -q`
                    ```
                    12:00:01 AM   runq-sz  plist-sz   ldavg-1   ldavg-5  ldavg-15   blocked
                    12:10:01 AM         0        98      0.00      0.00      0.00         0
                    Average:            0        98      0.00      0.00      0.00         0
                    ```
                    + Check for `runq-sz` > CPU count where `runq-sz` is the number of kernel threads in memory waiting for CPU to run.
            - Per-process
                * `cat /proc/<pid>/schedstat`
                    + Look at second field which is the time spent waiting on a runqueue.
        + Errors
            - Advanced, skip
    * Memory - capacity
        + Utilization
            - System-wide
                * `free -m`
                    ```
                                  total        used        free      shared  buff/cache   available
                    Mem:            983          81         297           0         604         750
                    Swap:             0           0           0
                    ```
                    + Check `Mem` (main memory) and `Swap` (virtual memory)
                * `vmstat 1`
                    ```
                    procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
                    r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
                    0  0      0 462720   2088 466352    0    0     1     5   15   31  0  0 100  0  0
                    ```
                    + Check `free` (main memory) and `swap` (virtual memory)
                * `sar -r`
                    ```
                    12:00:01 AM kbmemfree kbmemused  %memused kbbuffers  kbcached  kbcommit   %commit  kbactive   kbinact   kbdirty
                    12:10:01 AM    455608    551340     54.75      2088    429476    188988     18.77    206432    249844       288
                    12:20:01 AM    455376    551572     54.78      2088    429552    187700     18.64    206636    249912       288
                    Average:       455492    551456     54.77      2088    429514    188344     18.70    206534    249878       288
                    ```
                    + Check `%memused`
            - Per-process
                * `top`
                    ```
                    top - 00:27:59 up 3 days,  1:31,  1 user,  load average: 0.00, 0.09, 0.06
                    Tasks:  83 total,   1 running,  46 sleeping,   0 stopped,   0 zombie
                    %Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
                    KiB Mem :  1006948 total,   303580 free,    83832 used,   619536 buff/cache
                    KiB Swap:        0 total,        0 free,        0 used.   768608 avail Mem

                    PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
                        1 root      20   0  125560   5460   3932 S  0.0  0.5   0:06.66 systemd
                    ```
                    + Check `RES` (resident main memory), `VIRT` (virtual memory), `Mem` (system-wide summary)
        + Saturation
            - System-wide
                * `vmstat 1`
                    ```
                    procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
                    r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
                    0  0      0 303556   2024 617728    0    0     2     8   15   38  0  0 100  0  0
                    ```
                    + Check `si` (swap in from storage) and `so` (swap out from storage)
                * `sar -B`
                    ```
                    12:00:01 AM  pgpgin/s pgpgout/s   fault/s  majflt/s  pgfree/s pgscank/s pgscand/s pgsteal/s    %vmeff
                    12:10:01 AM      0.00      4.31     31.77      0.00     21.53      0.00      0.00      0.00      0.00
                    12:20:01 AM      0.11      3.14     23.31      0.00     16.59      0.00      0.00      0.00      0.00
                    ```
                    + Check `pgscank/s` (number of pages scanned by `kswapd` per second) + `pgscand/s` (number of pages directly scanned per second)
                    + Note: page scan happens when a process needs more memory and its not available so kernel scans pages to find ones that need to be paged out.
                * `sar -W`
                    ```
                    12:00:01 AM  pswpin/s pswpout/s
                    12:10:01 AM      0.00      0.00
                    12:20:01 AM      0.00      0.00
                    ```
                    + Check `pswpin/s` (number of pages swapped in from disk per second) and `pswpout/s` (number of pages swapped out to disk per second).
            - Per-process
                * `dmesg | grep killed`
                    + Checks for out-of-memory (OOM) killer
        + Errors
            - `dmesg` for physical failures
            - Dynamic tracing e.g., SystemTap `uprobes` for failed `mallocs()`
    * Network interfaces
        + Utilization: RX/TX throughput, max bandwidth
            * `sar -n DEV 1`
                ```
                12:00:01 AM     IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s
                12:10:01 AM        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00
                12:10:01 AM      eth0      0.24      0.26      0.02      0.03      0.00      0.00      0.00
                ```
                + Check `rxkB/s`/max (total kb received per second) and `txpck/s`/max (total kb transmitted per second).
                + Note: `/sys/class/net/eth0/speed` contains bandwidth
            * `ip -s link`
                ```
                1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
                    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
                    RX: bytes  packets  errors  dropped overrun mcast
                    1272       24       0       0       0       0
                    TX: bytes  packets  errors  dropped carrier collsns
                    1272       24       0       0       0       0
                2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
                    link/ether 0a:4a:ac:63:c1:dc brd ff:ff:ff:ff:ff:ff
                    RX: bytes  packets  errors  dropped overrun mcast
                    133729216  182324   0       0       0       0
                    TX: bytes  packets  errors  dropped carrier collsns
                    28794857   133109   0       0       0       0
                ```
                + Check `RX`/max and `TX`/max.
            * `cat /proc/net/dev`
                ```
                Inter-|   Receive                                                |  Transmit
                face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
                    lo:    1272      24    0    0    0     0          0         0     1272      24    0    0    0     0       0          0
                eth0: 133733246  182385    0    0    0     0          0         0 28800909  133163    0    0    0     0       0          0
                ```
                + Check `bytes` for `Receive` and `Transmit` and divide by max
            * `sar -n TCP,ETCP 1`
                ```
                12:17:19 AM  active/s passive/s    iseg/s    oseg/s
                12:17:20 AM      1.00      0.00  10233.00  18846.00

                12:17:19 AM  atmptf/s  estres/s retrans/s isegerr/s   orsts/s
                12:17:20 AM      0.00      0.00      0.00      0.00      0.00
                ```
                + Check `active/s` (number of locally-initiated TCP connections per second), `passive/s` (number of remotely-initiated TCP connections per second), `retran/s` (number of TCP retransmits per second)
        + Saturation
            * `ifconfig`
                ```
                eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9001
                inet 172.31.1.56  netmask 255.255.240.0  broadcast 172.31.15.255
                inet6 fe80::84a:acff:fe63:c1dc  prefixlen 64  scopeid 0x20<link>
                ether 0a:4a:ac:63:c1:dc  txqueuelen 1000  (Ethernet)
                RX packets 182633  bytes 133753995 (127.5 MiB)
                RX errors 0  dropped 0  overruns 0  frame 0
                TX packets 133368  bytes 28827704 (27.4 MiB)
                TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
                ```
                + Check `overruns` (number of received packets experiencing FIFO overruns caused by rate at which buffer gets full and kernel cannot empty it), `dropped` (total number of packets dropped by device driver)
            * `netstat -s`
                ```
                Tcp:
                    569 active connections openings
                    2662 passive connection openings
                    180 failed connection attempts
                    121 connection resets received
                    1 connections established
                    83008 segments received
                    87963 segments send out
                    3237 segments retransmited
                    1064 bad segments received.
                    29 resets sent
                    InCsumErrors: 1064
                ```
                + Check `segments retransmitted` which is an indication of packet loss
            * `sar -n EDEV`
                ```
                12:00:01 AM     IFACE   rxerr/s   txerr/s    coll/s  rxdrop/s  txdrop/s  txcarr/s  rxfram/s  rxfifo/s  txfifo/s
                12:10:01 AM        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
                12:10:01 AM      eth0      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
                ```
                + Check `EDEV`, `drop` (received and transmitted packets that are dropped) and `fifo` (received and transmitted packets put into a queue) metrics
            * `cat /proc/net/dev`
                ```
                Inter-|   Receive                                                |  Transmit
                face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
                    lo:    1272      24    0    0    0     0          0         0     1272      24    0    0    0     0       0          0
                eth0: 133768681  182835    0    0    0     0          0         0 28865553  133542    0    0    0     0       0          0
                ```
                + Check for `errs` and `drop`
            * Dynamic tracking for other TCP/IP stack queueing
        + Errors
            * `ifconfig`
                ```
                eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9001
                inet 172.31.1.56  netmask 255.255.240.0  broadcast 172.31.15.255
                inet6 fe80::84a:acff:fe63:c1dc  prefixlen 64  scopeid 0x20<link>
                ether 0a:4a:ac:63:c1:dc  txqueuelen 1000  (Ethernet)
                RX packets 188711  bytes 134356842 (128.1 MiB)
                RX errors 0  dropped 0  overruns 0  frame 0
                TX packets 139380  bytes 29949850 (28.5 MiB)
                TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
                ```
                + Check for `errors` and `dropped`
            * `netstat -i`
                ```
                Kernel Interface table
                Iface      MTU    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
                eth0      9001   188740      0      0 0        139410      0      0      0 BMRU
                lo       65536       24      0      0 0            24      0      0      0 LRU
                ```
                + Check for `RX-ERR` and `TX-ERR`
            * `ip -s link`
                ```
                2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
                link/ether 0a:4a:ac:63:c1:dc brd ff:ff:ff:ff:ff:ff
                RX: bytes  packets  errors  dropped overrun mcast
                134362980  188778   0       0       0       0
                TX: bytes  packets  errors  dropped carrier collsns
                29957873   139435   0       0       0       0
                ```
                + Check for `errors`
            * `sar -n EDEV`
                ```
                03:20:01 AM     IFACE   rxerr/s   txerr/s    coll/s  rxdrop/s  txdrop/s  txcarr/s  rxfram/s  rxfifo/s  txfifo/s
                03:30:01 AM        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
                03:30:01 AM      eth0      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
                ```
                + Check for `rxerr/s` and `txerr/s`
            * `cat /proc/net/dev`
                ```
                Inter-|   Receive                                                |  Transmit
                face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
                    lo:    1272      24    0    0    0     0          0         0     1272      24    0    0    0     0       0          0
                eth0: 134368396  188858    0    0    0     0          0         0 29974015  139508    0    0    0     0       0          0
                ```
                + Check for `errs` and `drop`
            * Dynamic tracing of driver function returns.
            * `dmesg | tail` for TCP dropping requests.
    * Storage I/O
        + Utilization: Device busy percent
            - System-wide
                * `iostat -xz 1`
                    ```
                    Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
                    xvda              0.00     0.05    0.07    0.69     1.63     7.67    24.64     0.00    4.07    0.96    4.38   0.16   0.01
                    ```
                    + Check for `%util` (percentage of CPU time during which I/O requests were issued to the device)
                * `sar -d`
                    ```
                    12:00:01 AM       DEV       tps  rd_sec/s  wr_sec/s  avgrq-sz  avgqu-sz     await     svctm     %util
                    12:10:01 AM  dev202-0      0.81      0.00      8.62     10.70      0.00      1.18      0.04      0.00
                    12:20:01 AM  dev202-0      0.58      0.23      6.28     11.32      0.00      0.34      0.02      0.00
                    ```
                    + Check for `%util` (percentage of CPU time during which I/O requests were issued to the device)
            - Per-process
                * `pidstat -d`
                    ```
                    04:30:47 AM   UID       PID   kB_rd/s   kB_wr/s kB_ccwr/s  Command
                    04:30:47 AM  1000      6046      0.00      0.00      0.00  pidstat
                    04:30:47 AM  1000     18113      0.80      3.60      0.31  bash
                    ```
                    + Check for `kB_rd/s` (kB read per sec) and `kB_wr/s` (kB written per sec)
                * `/proc/pid/sched`
                    + Check for `se.statistics.iowait_sum`
        + Saturation: Wait queue length
            - `iostat -xz`
                ```
                Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
                xvda              0.00     0.05    0.07    0.69     1.62     7.65    24.59     0.00    4.07    0.96    4.37   0.16   0.01
                ```
                + Check for `avgqu-sz` > 1 (average queue length of requests issued to device) or high `await` (average time in ms for I/O requests issued to the device to be served; this includes the time spent by requests in queue and time spent servicing them)
            - `sar -d`
                ```
                12:00:01 AM       DEV       tps  rd_sec/s  wr_sec/s  avgrq-sz  avgqu-sz     await     svctm     %util
                12:10:01 AM  dev202-0      0.81      0.00      8.62     10.70      0.00      1.18      0.04      0.00
                12:20:01 AM  dev202-0      0.58      0.23      6.28     11.32      0.00      0.34      0.02      0.00
                ```
                + Check for `avgqu-sz` > 1 or high `await`
        + Errors: Device errors
            - `/sys/devices/.../ioerr_cnt`
            - Dynamic/static tracing of I/O subsystem response codes.
    * Storage Capacity
        + Utilization
            - `free` for swap
                ```
                total        used        free      shared  buff/cache   available
                Mem:        1006948       84528      293232         404      629188      767788
                Swap:             0           0           0
                ```
            - `vi /proc/meminfo` for swap
                + Check `SwapFree`/`SwapTotal`
            - `df -h` for filesystem
        + Saturation: no checks because one its full you will get no space errors
        + Errors
            - `strace` for no space errors
            - `vi /var/log/messages` for errors
    * Controllers - storage, network cards
        * Skip; advanced
    * Interconnects - CPUs, memory, I/O
        * Skip; advanced
- Software Resources:
    * Mutex locks
        + Utilization is the time lock was held
            * With `CONFIG_LOCK_STATS=y` run `vi /proc/lock_stat`
            * Check `holdtime-total` / `acquisitions`
        + Saturation by threads queued waiting on lock
            * With `CONFIG_LOCK_STATS=y`, run `vi /proc/lock_stat`
            * Check `waittime-total` / `contentions`
    * Process/thread capacity
        + Utilization is usage of limited number of processes or threads
            * `top`
                + Check for `Tasks (current)`
                + `sysctl kernel.threads-max` to return total threads
        + Saturation if threads blocking on memory allocation
            * `sar -B`
                + Check for `pgscan`
        + Errors when allocation failed
            * `cant fork` errors
            * `pthread_create()` error
    * File descriptor capacity
        + Utilization
            - System-wide
                * `sar -v`
                    + Check `file-nr`
                    + `vi /proc/sys/fs/file-max` to get max file descriptors
            - Per-process
                * `ls /proc/<pid>/fd | wc -l`
                    + Compare against `ulimit -n`
        + Error
            - `strace`
                + Check for errors on system calls returning file descriptors e.g., `open()`, `accept()` etc
- Suggested Interpretations
    * Utilization
        + 100% is sign of a bottleneck
        + 70%+ can begin to be a problem:
            - If measured over a long time, it can hide short bursts of 100%
            - Some resources e.g., hard disks cannot be interrupted during operation; abovoe 70%, queueing delays can become more frequent and noticeable
    * Saturation
        + Any degree can be a problem
    * Errors
        + Non-zero errors worth investigating especially if they are increasing while performance is poor
- Cloud Computing
    * Software resource controls may limit tenants sharing system
    * Hypervisor or container (cgroup) limits for memory, CPU, network, storage I/O
- Strategy
    1. Start
    2. Identify resources
    3. Choose a resource
    4. Errors? If yes, investigate
    5. High utilization? If yes, investigate
    6. High saturation? If yes, investigate
    7. All resources checked? If no return to 3.
    8. Done

## The TSA Method (Source: http://www.brendangregg.com/tsamethod.html)

- For each thread, measure total time in different thread states.
    * `top -H -p <pid>`
        ```
        top - 07:14:15 up 6 days,  8:17,  1 user,  load average: 0.00, 0.00, 0.00
        Threads:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
        %Cpu(s):  0.0 us,  0.0 sy,  0.0 ni, 99.7 id,  0.0 wa,  0.0 hi,  0.0 si,  0.3 st
        KiB Mem :  1006948 total,   231052 free,    86732 used,   689164 buff/cache
        KiB Swap:        0 total,        0 free,        0 used.   762792 avail Mem
          PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
           1 root      20   0  125628   5464   3932 S  0.0  0.5   0:27.95 systemd
        ```
        * Executing = `us` + `sy` + `ni`
        * Runnable = `wa`
        * Anonymous paging = `stopped`
        * Sleeping = `sleeping`
        * Lock = `stopped`
        * Idle = `id`
- Investigate states from the most to least frequent with appropriate tools.
- Thread time divided into:
    1. Executing
        * Running on-CPU
        * Split into user and kernel time
        * For user time, `CPU profilers` (e.g., flame graphs) identify hot code paths
        * For system time examine system call rates using `strace` or `dtrace`
    2. Runnable
        * Run queue latency
        * Check system-wide CPU utilization and saturation with `USE`
    3. Anonymous paging (swapping)
        * Runnable but either swapped out or paged out, waiting for residency
        * Check system-wide main memory availability with `USE`
        * Look for paging and swapping memory saturation metrics with `USE`
    4. Sleeping
        * Waiting for I/O including network, blck, data/text page-ins
        * Check system calls (identify time in system calls and related resources; check `mmap()` and non-system call I/O via mappings)
        * Check resource usage to identify busy resources
        * Check thread blocking (see off CPU performance analysis)
        * `iostat`
    5. Lock
        * Waiting to acquire a synchronization lock (waiting for someone else)
        * Identify the lock thread is waiting on and the reason it took time to acquire
    6. Idle
        * Waiting for work
        * Check client load applied
        * Various reasons for idleness e.g., waiting for new network connection, network I/O, a locl, timer; difficult to identify idle state
- Example 1:
    * Application has performance issue. TSA measures thread state time for application threads in each of the six states. 50% time spent runnable, waiting for turn on CPU. USE shows CPU limit reached. Solution is to increase CPU limit.
- Example 2:
    * MySQL is slow. TSA measures thread state time for MySQL. Shows large percentage of time spent runnable, waitind for other applications stealing CPU cycles.
- Document shows how to use `prstat` in Solaris but no Ubuntu/centos equivalent
- Create Flame graph to visualize codepaths consumed CPUs
    * x-axis: stack profile population (wider = more often it was in stacks)
    * y-axis: stack depth
    * Find long running functions
- `perf record -F <sample rate> -p <pid>` Linux profiler
    * Visualize as a Flame graph

## Network Troubleshooting (Source: Chapter 10 Systems Performance)

### Packet Sniffing

- Capture packets from network so protocol headers and data can be inspected.
- Information captured:
    * Timestamp
    * Packet including header (ethernet, IP, TCP), partial or full payload data
    * Metadata including number of packets, drops
- `tcpdump -ni eth0`
    ```
    03:40:58.864678 IP 172.31.1.56.ssh > 98.234.62.159.51174: Flags [P.], seq 1128733:1128945, ack 648, win 275, options [nop,nop,TS val 3878900561 ecr 678600419], length 212
    03:40:58.864718 IP 172.31.1.56.ssh > 98.234.62.159.51174: Flags [P.], seq 1128945:1129157, ack 648, win 275, options [nop,nop,TS val 3878900561 ecr 678600419], length 212
    03:40:58.869297 IP 98.234.62.159.51174 > 172.31.1.56.ssh: Flags [P.], seq 648:684, ack 1092005, win 3496, options [nop,nop,TS val 678600421 ecr 3878900530], length 36
    ```

### Static Performance Tuning

- Number of network interfaces in use
- Max speed of network interfaces
- Half or full duplex network interfaces
- MTU configured for network interfaces
- Is forwarding enabled?
- Software imposed network throughput limits (important for cloud computing)

### Resource Controls

- Network bandwidth limits for different connections, processes, groups of processes applied by the kernel.
- Priorization of network traffic (IP QoS). Higher priority to traffic between clients and server.

### Analysis

- `netstat` discussed in USE
- `sar` discussed in USE
- `ifconfig` discussed in USE
- `ip` discussed in USE
- `nicstat` discussed in USE
- `ping`
    ```
    PING http2.joyent.map.fastly.net (151.101.53.63) 56(84) bytes of data.
    64 bytes from 151.101.53.63 (151.101.53.63): icmp_seq=1 ttl=40 time=9.59 ms
    ```
    + Round trip time
    + Note: ICMP treated lower priority so latency may be higher than usual
- `traceroute`
    ```
    traceroute to google.com (172.217.14.206), 30 hops max, 60 byte packets
    1  ec2-34-221-151-233.us-west-2.compute.amazonaws.com (34.221.151.233)  13.322 ms ec2-34-221-151-229.us-west-2.compute.amazonaws.com (34.221.151.229)  0.722 ms ec2-34-221-151-235.us-west-2.compute.amazonaws.com (34.221.151.235)  99.840 ms
    2  100.65.40.32 (100.65.40.32)  5.396 ms 100.66.8.168 (100.66.8.168)  19.960 ms 100.66.8.180 (100.66.8.180)  12.572 ms
    3  100.66.18.240 (100.66.18.240)  8.138 ms 100.66.20.8 (100.66.20.8)  5.079 ms 100.66.19.38 (100.66.19.38)  21.567 ms
    ```
    + Increases TTL by one for each packet causing sequence of gateways to the host to reveal themselves by sending ICMP time exceeded response messages
    + Three RTTs
    + Check for increased latencies for certain paths
- `tcpdump` see previous section
- Wireshark
    * Used to analyze `tcpdump` pcap files.
    * Useful features:
        + Identify network connections and related packets
        + Translation of hundreds protocol headers
- `strace <pid>` to trace socket-related syscalls

## Examples

### In-house tool "running slow" on production server.

- Problem report:
    * Actual behavior: tool is running slow on the production server.
    * Expected behavior: tool should be running faster returning results quicker.
    * Questions:
        - Were there changes pushed out to the tool recently?
            + If yes, these changes may have caused performance degradation.
            + A rollback may be necessary to triage, and further analyses e.g., TSA method, dynamic tracing, profiling may be used by developers to further diagnose performance hit.
        - Is the tool being run in an anticipated manner?
            + For example, a poorly formed database query could take a long time to run and eat up resources.
- Triage:
    * Migrate user to a new server, if no recent changes to the tool. Possible physical resource problems (i.e., CPU, memory, networking, storage) on the problematic server.
    * If recent changes made, a rollback should occur, and further analysis should be performed on the performance degradation incurred.
- Examine/Diagnose/Treat:
    * High level
        + Check application logs for possible errors (possibly due to recent update).
    * USE method
        + CPU
            - Is systemwide utilization high? `vmstat`, `sar -u`, `uptime` looking for %cpu time in use.
            - If so, check for the specific process utilization `top`, `pidstat`.
            - If utilization is high, then check for saturation `vmstat`, `sar -q` to check for processes waiting in queue.
            - Also check for the average time the process is waiting in queue in `/proc/pid/schedstat`.
            - If we see signs of CPU saturation, we could either scale horizontally or vertically depending on the nature of the tool.
                + Scale horizontally if the tool is parallelizable; otherwise vertically.
            - If the tool was running fine before a given change, we could also jump to the TSA method to further analyze these processes.
                + For example, use CPU profiler to determine code hot paths (i.e., portions in the code that eats up the most CPU time).
                + Note: performance of the tool may be best left up to the developers.
            - Note: hardware problems may also be possible (check `dmesg`).
        + Memory
            - Is systemwide utilization high? `free -m`, `vmstat`, `sar -r` looking for %memory used and memory swap.
            - If so, check for specific process utilization `top` looking for virtual and resident main memory usage.
            - If utilization is high, then check for saturation `vmstat`, `sar -B`, `sar -W` looking for pages scanned and pages swapped.
                + Recall that pages scanned by the kernel occurs when the kernel needs to scan pages in use to evict for new processes.
            - If we see signs of satuation, we could either scale horizontally or vertically depending on the nature of the tool (same as CPU).
            - If the tool was running fine before a given change, we could use dynamic tracing `bpftrace` to find errors e.g., `malloc` errors.
                + Note: performance of the tool may be best left up to the developers.
            - Note: hardware problems may also be possible (check `dmesg`).
        + Network
            - Is systemwide utilization high? `sar -n DEV`, `ip -s link`, `sar -n TCP,ETCP` looking for kB received and transmitted per second, number of TCP connections and number of retransmits per second.
            - If utilization is high, then check for saturation `ifconfig`, `netstat -s`, `sar -n EDEV` looking for dropped packets, packets that are put into FIFO queue because kernel cannot handle them quick enough, retransmits.
            - If saturation occurs, look for errors `ifconfig`, `netstat -i`, `ip -s link`, `sar -n EDEV` looking for received and transmitted errors.
            - If we signs of saturation or errors, we could again scale up or horizontally to increase bandwidth of the network interface cards.
            - If the tool was running fine before a given change, we could use dynamic tracing `bpftrace` to find networking driver errors.
                + Note: performance of the tool may be best left up to the developers.
            - Note: hardware problems may also be possible (check `dmesg`).
        + Storage I/O
            - Is systemwide utilization high? `iostat -xd`, `sar -d` looking for %util which is the CPU time spent issuing I/O commands.
            - If so, check per process `pidstat -d` looking for kb read and kb write per second.
            - If utilization is high, then check `iostat -xd`, `sar -d` looking for average queue length of requests issued to device.
            - If we see signs of saturation, we may want to consider increasing the storage size to increase I/O.
            - If the tool was running fine before a given change we could use dynamic tracing `bpftrace` to see why the number of system calls to storage increased.
            - Note: hardware problems may also be possible (check `dmesg`).
        + Storage capacity
            - Is systemwide utilization high? `df -h` looking for capacity.
            - If utilization is high then look for no space errors in `bpftrace` or in `/var/log/messages`.
            - If we see errors then clear unnecessary files or increase storage capacity.

### Client cannot connect to server.

- Problem report:
    * Actual behavior: Client does not receive any response when accessing a server via HTTP.
    * Expected behavior: Client should receive a 200 response with html in the payload from the server.
    * Questions:
        + Where is the client located?
            - Typically, we should have a geographic-based monitoring tool like Pingdom in all user locations that check for page load time and size, and alert for discrepancies.
        + Can we reproduce the error?
            - To troubleshoot this type of network issue, we would need to coordinate with the client or be able to spin up a server in the client's local network.
- Triage:
    * Spin up another server or direct client to another server while we troubleshoot.
    * If client cannot access secondary server, most likely a network issue between client and data center e.g., ISP which we cannot solve.
- Examine/diagnose/treat:
    * Initial thoughts:
        + If the client does not receive any response, this suggests a connection was never made to the server at all.
        + This could be an issue with DNS, a network component between the client and server, or firewall issue on the server side.
        + Let's assume for this example, the client is connecting directly to the server with IP (no DNS).
    * Network diagnostics
        + First run `ping <server-ip>` for sanity check
            - Assume no response.
        + Next run `traceroute <server-ip>` to see if connection is lost somewhere along the way from client to server
            - Assume traceroute never receives the final server response.
        + Can a known whitelisted IP access the contents e.g., from a known office IP?
            - If yes:
                * Verify the client IP is not blocked/firewalled (e.g., check `iptables`), update if necessary.
                * Otherwise, network issue is upstream of server, between client and server which we cannot handle e.g., ISP connection issues.
            - If no:
                * Is the port (80) open on the server and listening for TCP connections? Use `lsof -i -P`
                * Is `httpd` running? Use `ps | grep httpd` to verify.
                * Is `httpd` healthy? Use `journalctl -u httpd` or check `/var/log/messages` for any errors.
                * If we still cannot find the issue, then apply USE to see if there is a resource bottleneck preventing httpd from serving traffic correctly.
                * If no bottleneck is found, then we need to perform dynamic tracing and cpu profiling on httpd process for application level problems.

### Client high latency response in loading page.

- Problem report:
    * Actual behavior: Client page loads taking very long.
    * Expected behavior: Client page loads should be shorter.
    * Questions:
        + Where is the client located?
            - Same as previous example, we need to work with client or set up a server in their local network to diagnose.
        + Can we reproduce the error?
- Triage:
    * Spin up another server or direct client to another server while we troubleshoot.
    * If possible, in a different geographic location.
    * If latency still persists then this is not a server side issue.
- Examine/diagnose/treat:
    * Initial thoughts:
        + Latency can be caused by one or more hosts between the client and server.
        + Latency can also be caused server side by slow reponse time (e.g., slow database queries).
    * Network diagnostics:
        + First run `ping <server-ip>` for sanity check.
            - Assume normal response.
        + Next run `traceroute <server-ip>` to see if there is a large latency at any intermediate point.
            - If yes, the latency may be bottlenecked by that hop.
            - If no, most likely latency is server side.
                * Perform USE method to see if there are any resource bottlenecks (most likely network).
                * If no bottleneck is found, then we need to perform dyanmic tracing and cpu profiling for services running for application level problems.

### Client 404 from web server.

- Problem report:
    * Actual behavior: Client receieves 404 response from webserver.
    * Expected behavior: Client should receieve 200 response with html payload.
    * Questions:
        + Can we reproduce the error?
            - This problem most likely does not deal with geographic location of the client unless there is geographically-dependent content.
- Triage:
    * Direct client to another server.
    * If 404 still persists then possibly rollback to last working state.
- Examine/diagnose/treat:
    * Initial thoughts:
        + A 404 response indicates the client can successfully connect to the server.
        + A 404 response indicates the URI provided is trying to access a resource that cannot be found.
    * Sanity checks
        + Look in access logs for user IP and verify that entries have been made for user IP and 404 return code issued.
        + Look in error logs to find the resource that was not found.
        + Verify that the resource does not exist.
            - For example, if resource is a local static file on server, verify it exists and that permissions are correct (i.e., webserver can access it).
    * If everything looks correct above, apply USE method to look for resource bottlenecks.
        + This seems unlikely for this scenario but possibly storage I/O prevents files from being read, etc.

### Client 500 from web server.

- Problem report:
    * Actual behavior: Client receieves 500 response from webserver.
    * Expected behavior: Client should receieve 200 response with html payload.
    * Questions:
        + Can we reproduce the error?
- Triage:
    * Direct client to another server.
    * If 500 still persists then possibly rollback to last working state.
- Examine/diagnose/treat:
    * Initial thoughts:
        + A 500 response indicates the client can successfully connect to the server.
        + A 500 response indicates internal server error.
    * Sanity checks
        + Look in access logs for user IP and verify that entries have been made for user IP and 500 return code issued.
        + Look in error logs for futher clues.
    * If error logs do not show the problem, apply USE method to look for resource bottlenecks.
    * Could also be an issue with a downstream service e.g., database.
        + We would have to work through each of the downstream components applying USE method, and looking for application level errors.
        + Also be careful of cascading failures between components.