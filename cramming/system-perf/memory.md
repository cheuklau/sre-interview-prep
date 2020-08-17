# Memory

## Introduction

- Main memory stores apps and kernel instructions, their working data and file system caches
- Once main memory is filled, system switches data between memory and storage device
- System may also terminate largest memory-consuming processes
- CPU expense in allocating/freeing memory, copyin gmemory and managing memory address space mappings
- Note: on-CPU memory caches are covered in CPUs

## Terminology
- Main memory: physical memory; fast data storage area provided as `DRAM`
- Virtual memory: abstraction of main memory that is infinite and non-contended
- Resident memory: memory that currently resides in main memory
- Anonymous memory: memory with no filesystem location or path; includes working data of a process address space called the heap
- Address space: memory context; virtual address space for each process and for kernel
- Segment: area of memory flagged for a particular purpose e.g., storing executable
- OOM: out of memory; kernel detects low memory
- Page: unit of memory used by OS and CPUs; 4 or 8 kbytes
- Page fault: invalid memory access
- Paging: transfer of pages between main and storage devices
- Swapping: Swapping refers to paging to the swap device (transfer of swap pages); this book defines swapping as transfer of entire process from main to swap devices
- Swap: on-disk area for paged anonymous data and swapped processes

## Concepts

### Virtual memory

- Provides each process and kernel with its own large, linear private address space
- Simplifies software development, leaving physical memory placement for OS to manage
- Supports:
    * Multi-tasking as virtual address spaces are separated by design
    * Oversubscription since in-use memory can extend beyond main memory
- Process address space mapped by virtual memory subsystem to main memory and physical swap device
- Pages of memory moved between them by the kernel as needed (i.e., paging) allowing kernel to oversubscribe main memory
- Kernel may impose a limit to oversubscription

### Paging

- Movement of pages in and out of main memory
- Allows:
    * Partially loaded programs to execute
    * Programs larger than main memory to execute
    * Efficient movement of programs between main memory and storage devices
- Paging is a fine-grained approach to managing and freeing main memory since page size is relatively small (4kbytes)
    * This is unlike swapping out entire processes
- Filesystem paging
    * Caused by reading and writing of pages in memory-mapped files
    * Normal for applications using file memory mappings `nmap()` and on filesystems that use page cache (most do)
    * Kernel can free memory by paging some out
    * This is good swapping
- Anonymous paging
    * Data that is private to processes e.g., process heap and stacks
    * Anonymous term because it has no named location in the operating system (i.e., no filesystem path)
    * Anonymous page-outs require moving the data to the physcial swap devices
    * Swapping refers to this type of paging
    * Hurts performance because when apps access memory pages that have been paged out, they block disk I/O required to read them back to main memory
    * Anonymous page-in adds latency to app
    * Performance best when there is no anonymous paging
        + Configure apps to remain within main memory available
        + Monitor page scanning, memory utilization and anonymous paging

### Demand Paging

- Demand paging map pages of virtual memory to physical mmory on-demand
- Defers CPU overhead of creating mappings until they are actually needed and accessed
- Sequence:
    1. Write to a newly allocated page of virtual mapping
    2. MMU performs lookup but no mapping is found between virtual and physical memory
    3. MMU issues a page fault (i.e., page accessed when there is no page mapping)
    4. MMU performs on-demand mapping to physical memory for process address space (virtual memory)
- Note that step 1 could also have been a read in the case of a mapped file which contains data but isn't mapped yet to this process address space
- Minor faults are mappings that can be satisfied from another page in memory
- Major faults are mappings that require storage device access
- Any page of virtual memory has one of the following states:
    1. Unallocated
    2. Allocated, but unmapped
    3. Allocated and mapped to main memory (RAM)
    4. Allocated and mapped to the physical swap device (disk) - page is paged out due to system memory pressure
- State 1 to 2 to 3 is a page fault; if it requires disk I/O it is a major page; otherwise minor page
- Two memory usage terms:
    * Resident set size (RSS): size of allocated main memory pages (3)
    * Virtual memory size: size of all allocated areas (2 + 3 + 4)

### Overcommit

- Allows more memory to be allocated than system can store (more than physical and swap combined)
- Relies on demand paging and tendency of apps to not use much of the memory they have allocated
- Applications request for memory (e.g., `malloc()`) will succeed when they would have otherwise failed
- App can allocate memory generously then later use it sparsely on demand
- Overcommit can be tuned

### Swapping

- Movement of entire processes between main memory and physical swap device
- All of its private data is written to swap device (e.g., thread structures and process heap)
- To swap process back in, kernel takes into account thread priority, the time it was waiting on disk and the size of the process
- Long-waiting and smaller processes are favored
- Swapping hurts performance because a process that has been swapped out requires numerous disk I/O to run again
- LINUX SYSTEMS DO NOT SWAP PROCESSES AT ALL AND RELY ONLY ON PAGING.
- WHEN PEOPLE SAY THE SYSTEM IS SWAPPING THEY USUALLY MEAN PAGING.
- ON LINUX, THE TERM SWAPPING REFERS TO PAGING TO THE SWAP FILE OR DEVICE.

### File System Cache Use

- Normal for memory to grow after system boot as OS uses available memory to cache filesystem
- If there is spare main memory, then use it for something useful
- Kernel should be able to quickly free memory from file system cache when applications use it

### Utilization and Saturation

- Main memory utilization is used memory versus total memory.
- Memory used by file system cache can be treated as unused.
- If demand for memory exceeds amount of main memory, main memory becomes saturated.
- OS frees memory by paging, swapping and the OOM killer.
- Virtual memory can also be studied in terms of capacity utilization if system imposes a limit on the amount of virtual memory it is willing to allocate
- Once virtual memory is exhausted, kernel will fail allocations e.g., `malloc()` returns `ENOMEM`
- Currently available virtual memory on a system is sometimes called available swap

### Allocators

- Actual allocation and placement inside of virtual address space is done with allocators
- User-land libraries or kernel-based routines e.g., `malloc()` or `free()`

### Word Size

- CPU processors may support multiple word sizes e.g., 32-bit and 64-bit
- Address space size is bounded by the addressable range from the word size
- Applications requiring more than 4GB are too large for a 32-bit address space and need to be compiled for 64-bits or higher

## Architecture

### Main Memory

- Dynamic random-access memory (DRAM)
- Contents lost when power is lost
- High-density storage as each bit is implemented using only two logical components: capacitor and transistor
- Access time of main memory measured as the column address strobe (CAS) latency
    * For DDR3 it is around 10 ns
