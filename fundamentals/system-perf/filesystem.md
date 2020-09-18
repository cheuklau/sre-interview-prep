# Filesystems

## Terminology

- Filesystem: Organization of data as files and directories with a file-based interface for accessing them and file permissions to control access
- Filesystem cache: Area of main memory (DRAM) used to cache file system contents
- Operations: `read()`, `write()`, `open()`, `close()`, `stat()`, `mkdir()` and others
- I/O: Operations that directly read and write including `read()`, `write()`, `stat()` and `mkdir()`
- Logical I/O: I/O issued by the application to the filesystem
- Physical I/O: I/O issued directly to disks by the file system
- Throughput: Current data transfer rate between applications and the file system (bytes per second)
- Inode: Index node (inode) is a data structure containing metadata for a file system obejct including permissions, timestamps, data pointers
- VFS: virtual filesystem; kernel interface to abstract and support different file system types
- Volume manager: software for managing physical storage devices in a flexible way creating virtual bolumes from the for use by OS

## Models

### Filesystem Interfaces

- Applications interface with filesystem via logical object operations e.g., `read()`, `write()` etc
- System tools interact with the filesystem via logical admin operations e.g., `mount()`, `umount()` etc
- Filesystem interacts with the storage devices (disks) via physical operations

## Concepts

### Filesystem Latency

- Primary metric of file system performance
- Measured as the time from a logical filesystem request to completion
- Includes time spent in the file system, kernel disk I/O sysbsystem and waiting on disk devices (physical I/O)
- App threads often block during an app request to wait for file system requests to complete
    * Therefore, filesystem latency directly and proportionally affects app performance!
- Cases where apps not affected including use of non-blocking I/O or when I/O is issued from an asynchronous thread
- Use tracing to find which application routine issued the logical file system I/O

### Caching

- After boot, file system uses main memory as a cache to improve performance
- Reduces logical I/O latency since it can be served from memory rather than disk
- When apps need more memory, kernel quickly frees it from the filesystem cache for use
- Filesystem caching improves read performance and buffering to improve write performance

### Random vs Sequential I/O

- A series of logical filesystem I/O is either random or sequential
- Sequential I/O: next I/O begins at the end of the previous I/O
- Random I/O have no apparent relationship between them and offset randomly changes
- Due to performance characteristics of certain storage devices, file systems have attempted to reduce random I/O by placing file data on disk sequentially and contiguously
- Fragmentation describes when a file system does this poorly causing file placement to be scattered over a drive so that sequential logical I/O yields random physical I/O

### Prefetch

- Detect a sequential read workload based on the current and previous file I/O offsets
- Predict and issue disk reads before app has requested them
- Populates the file system cache so that if app does perform the expected read it results in a cache hit
- Also known as read-ahead

### Write-Back Caching

- Treats writes as completed after the transfer to main memory and writing them to disk sometime later asynchronously
- Filesystem process for writing data to disk is called flushing
- Sequence:
    1. App issues `write()` passing execution to the kernel
    2. Data from app address space copied into the kernel
    3. Kernel treats `write()` syscall as complete, passing execution back to the app
    4. Sometime later, asynchronous kernel task finds written data and issues disk writes
- Note: this trades off reliability since DRAM is volatile dirty data can be lost during power failure

### Synchronous Writes

- Completes only when fully written to persistent sotrage
- Much slower than asynchrounous writes (write-back caching) but improves reliability
- `fsync()` can be used to group synchronous writes to improve performance

### Raw and Direct I/O

- Raw I/O
    * Issued directly to disk offsets, bypassing filesystem altogether
    * Used by some apps e.g., databases that can manage and cache their own data better than file system cache
- Direct I/O
    * Allows apps to use a filesystem but bypass file system cache
    * Similar to synchronous writes

### Non-Blocking I/O

- Normally file system I/O will either completely immediately from cache or after waiting for disk I/O
- If waiting is required, app thread will block and leave CPU, allowing other threads to execute while it waits
- While blocked thread cannot perform work, this typically isn't a problem since multi-threaded apps can create additional threads to execute while some are blocked
- In some cases, non-blocking I/O is desired e.g., to avoid overhead of thread creation
- Performed by using `O_NONBLOCK` or `O_NDELAY` flags to `open()` syscall
- Causes reads and writes to return an `EAGAIN` error instead of blocking which tells app to try again later

### Memory-Mapped Files

- For some apps, file system I/O can be improved by mapping files to the process address space and accessing memory offsets directly
- Avoids syscall execution and context switch when calling `read()` or `write()` to access file data
- Memory mapping created using `mmap()` and removed with `munmap()`

### Metadata

- Data describes contents of files and directories
- Metadata describes info about them
- Logical metadata:
    * Info read and written to file system by apps
    * Explictly e.g., reading file stats `stats()`, creating and deleting files (`creat()`, `unlink()`) and directories (`mkdir()`, `rmdir()`)
    * Implicitly e.g., file system access time stamps, directory modification time stamps

### Physical Metadata

- On-disk layout metadata necessary to record all file system information

### Special File Systems

- Special filesystems e.g., temporary files `/tmp`, kernel device paths `/dev` and system statistics `/proc`

### Capacity

- When file systems fill, performance may degrade for a couple of reasons
- When writing new data, takes more time to locate free blocks on disk
- Areas of free space on disk likely to be smaller and more sparesely located degrading peformance due to smaller I/O or random I/O

## Methodology

## Disk Analysis

- Ignore filesystem and focus on disk performance
- Assumes worst I/O is disk I/o
- Typically works with simpler file systems and smaller caches

## Latency Analysis

- Measure latency of filesystem operations
    1. Application
    2. Syscall interface
    3. VFS
    4. Top of file system

