# Disks

## Introduction

- Under high load, disks become a bottleneck leaving CPUs idle as system waits for I/O to complete
- Disks are the primary storage device of systems e.g., magnetic rotating disks and flash memory based solid state disks
- SSDs improve disk I/O performance

## Terminology

- Virtual disk: emulation of storage device
- Transport: physical bus used for communication including data transfers (I/O) and other disk commands
- Sector: Block of storage on disk (typically 512 bytes)
- I/O: reads and writes only; consists of direction (read or write), disk address (location) and a size (bytes)
- Throughput: current data transfer rate (bytes per second)
- Bandwidth: maximum possible data transfer rate for storage transports or controllers
- I/O latency: time for an I/O operation
- Latency outliers: disk I/O with unusually high latency

## Models

### Simple Disk

- On-disk queue for I/O requests
- Flash memory based disks can have separate queues for read and write I/O

## Caching Disk

- On-disk cache allows some read requests to be satisfied from a faster memory type
- Small DRAM on physical disk device
- May also be used to improve write performance by using it as a write-back cache (signal as write complete after data transfer to cache before slower transfer to disk)
- Write through cache which completes after only full transfer to next level

## Controller

- Simple type of disk controller bridges CPU I/O transport with storage transport attached to disk devices
- Also called host bus adaptors (HBAs)

## Concepts

### Measuring Time

- Response time for storage devices (disk I/O latency) is time from I/O request to completion
    * Service time: time I/O takes to be serviced excluding wait time in queue
    * Wait time: time I/O waits in queue
- Service time from the block device interface is typically treated as a measure of disk performance (e.g., `iostat`)

### Calculating Time

- Disk service time typically not observable by OS directly
- Average disktime can be inferred as: utilization / IOPS e.g., utilization of 60% and IOPS of 300 gives average service time of 600ms/300IOPS = 2ms

## Time Scales

- On-disk cache hit is `< 100us`
- Flash memory read is `100 to 1000us`
- Rotational disk sequential read is `1ms`
- Random disk read is `8ms`
- Typically anything above `10ms` can be a bottleneck; exception is web-facing applications where there is already high latency between netowrk and client browser that disk I/O only becomes an issue beyond `100ms`

## Random vs sequential I/O

- Disk I/O workload is random or sequential based on relative location of the I/O on disk (disk offset)
- Sequential workloads are streaming workloads (streaming reads and writes to disk)
- Random I/O incurs additional latency as the disk heads seek and the platter rotates between I/O (for magnetic rotational disk)
- Other disk types e.g., flash-based SSD perform no differently between random and sequential I/O patterns

## Read/Write Ratio

- Ratio of reads to writes (IOPS or throughput)
- Helps when designing and configuring systems
- System with high read rate may benefit more from adding cache
- System with high write rate may benefit more from adding more disks to increase max available throughput and IOPS
- Reads may be random I/O while writes may be sequential

## I/O Size

- Average I/O size (bytes) or distribution of I/O sizes should be characterized
- Larger I/O sizes provide higher throughput but longer per-I/O latency
- I/O size may be altered by disk device subsystem
- Ideal size documented by disk vendor (e.g., flash may have 4KB read and 1MB write as optimal)

## IOPS are not Equal

- IOPS are not created equal and cannot be directly compared between devices and workloads
- Example, rotational disk workload of 5000 sequential IOPS may be faster than one of 1000 random IOPS
- Flash IOPS also hard to compare since I/O Performance is often relative to I/O size and direction (read or write)

## Utilization

- Calcualted as the time a disk was busy performing work during an interval
- Disk at 0% utilization is idle and 100% is continually busy performing I/O and other disk commands
- Disks at 100% utilization are a bottleneck
- May be a point between 0 and 100% where disk performance is no longer satisfactory due to increased queueing either on disk queues or OS
- Exact value depends on disk, workload and latency requirements

## Virtual Disk Utilization

- For virual disks supplied by hardware (e.g., disk controller), the OS may be aware only of when virtual disk was busy but know nothing about performance of underlying disks
- For example, virtual disks that include a write-back cache may appear less busy than the underlying disks really are

## Saturation

- Measure of queued work beyond what resource can deliver
- Calculated as the average length of the device wait queue in the OS
- Important to know exactly what caused 100% utilization; can use tracing to examine I/O events

## I/O Wait

- I/O wait is a per CPU performance metric showing time spent idle when there are threads on CPU dispatcher queue (sleepingt) that are blocked on disk I/O
- High rate of I/O wait per CPU shows disks may be a bottleneck
- I/O wait can be confusing
    * Example: If another CPU-hungry process comes along, I/O wait will drop since CPUs now have something to do instead of being idle; however I/O is still present and blocking threads despite the drop in I/O wait metric
    * Example: If software upgrade improves efficiency and uses fewer CPU cycles, revealing I/O wait; this may lead to believe that upgrade caused disk issues when in fact disk issue is the same
- More reliable metric is the time that application threads are blocked on disk I/O - caputred with static or dynamic tracing.

## Synchronous vs. Asynchronous

- Disk I/O latency may not directly affect applciation performance if the app I/O and disk I/O operate asynchronously
- Occurs frequently with write-back caching
- Apps may use read-ahead to perform asynchronous reads which may not block app while disk completes the I/O

## Disk vs App I/O

- Disk I/O is the end result of various kernel components including file systems and device drivers
- May reasons why rate and volume of disk I/O may not match I/O issued by app:
    * File system inflation, deflation and unrelated I/O
    * Paging due to system memory shortage
    * Device driver I/O size: rounding up I/O size or fragmenting I/O

## Methodologies

### Tools method

- `iostat`
    * Looks for busy disks (60% utilization)
    * High average service times (10ms)
    * High IOPS
- `iotop`
    * Identify which process causing disk I/O
- Dynamic tracing
    * Disk I/O latency in detail