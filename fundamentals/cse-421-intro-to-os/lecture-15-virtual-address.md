# Lecture 15

## Convention

- Process layout is specified by the executable and linker format (ELF)
- Some layouts is the function of convention
- Example: why not load the code at `0x0`
    * To catch possibly the most common programmer error i.e., NULL pointer problems
    * Leaving a large portion of the process address space starting at `0x0` empty allows kernel to catch these errors

## Destined to Ever Meet?

- Stack starts at the top of the address space and grows down
- Note: registers are on the CPU
- Heap starts towards the bottom and grows up
- Will the stack and heap ever meet?
    * Probably not because that would mean either stack or heap was huge

## Relocation

- Given our address space model, no more problems with locating things, right?
    * Not quite; dynamically loaded libraries still need to be relocated at run time

## Address Space: A Great Idea?

- Address space abstraction sounds powerful and useful
- Can we implement it? What is required?
    * Address translation:
        + Example: `0x100000` to process 1 is not the same as `0x10000` to process 2 is not the same
    * Protection:
        + Address spaces are intended to provide a private view of memory to each process
    * Memory management
        + Together one or several processes may have more address space allocated than physical memory on the machine
- Implementing address sapaces requires breaking the direct connection between a memory address and physical memory
- Introducing another level of indirection is a classic systems techniques (e.g., for file handles)
- Forcing processes to translate a reference to gain access to the underlying object provides the kernel with a great deal of control
- References can be revoked, shared, moved and altered

## Memory Interface

- We don't usually think about memory as having an interface but it does
    * `load(address)`: load data from the given address, usually into a register or possibly into another memory location
    * `store(address, value)`: store value to the given address where value may be in a register or another memory location
- Address space abstraction requires breaking the connection between a memory address and physical memory
- We refer to data accessed via the memory interface as using virtual addresses
    * Physical address points to memory
    * Virtual address points to something that acts like memory
- Virtual addresses have a much richer semantics than physical addresses, encapsulation location, permanence and protection

## Virtual Addresses: Location

- Data referenced by a virtual address might be
    * In memory: but kernel may have moved it to the disk
- Virtual address --> physical address
    * On-disk but the kernel may be caching it in memory
- Virtual address --> disk, block, offset
    * In memory on another machine
- Virtual address --> IP address, physical address
    * On a port on a hardware device
- Virtual address --> device, port

## Virtual Addresses: Permanence

- Processes expect data written to virtual addresses that point to physical memory to store values trannsiently
- Processes expect data written to virtual addresses that point to disk to store values

## Virtual Addresses: Permissions and Protection

- Some virtual addresses may only be used by the kernel while in kernel mode
- Virtual addresses may also be assigned read, write or execute permissions
    * `read/write`: process can load/store to this address
    * `execute`: process can load and execute instructions from this address

## Creating Virtual Addresses: exec()

- `exec()` uses a blueprint from an ELF file to determine how the address space should look when `exec()` completes
- `exec()` creates and initializes virtual memory that point to memory:
    * Code: usually marked as read-only
    * Data: marked as read-write, but not executable
    * Heap: area used for dynamic allocations, marked read-write
    * Stack: space for the first thread
- Recall: `pmap <pid>` to look at memory mappings
    * `pmap` shows virtual addresses so multiple instances of the same process will have the same virtual addresses
    * `pmap` does not show you where those virtual addresses point

## Creating Virtual Address: fork()

- `fork()` copies the address space of the calling process
- The child has the same virtual addresses aas the parent but they point to different memory locations
- Copying all the memory is expensive
    * Especially when the next thing that a proces does is to load a new binary which destroys most of the copied state

## Creating Virtual Addresses: sbrk()

- Dynamic memory allocation is performed by `sbrk()` system call
- `sbrk()` asks the kernel to move the breakpoint or the point at which the process heap ends
- Used by `malloc()` when it wants more heap

## Creating Virtual Addresses: mmap()

- `mmap()` is a system call that creates virtual addresses that map to a portion of a file

## Example Machine Memory Layout: System/161

- System/161 emulates a 32-bit MIPS architecture
- Addresses are 32-bits wide: from 0x0 to 0xFFFFFFFF
- MIPS architecture defines four address regions:
    1. 0x0 to 0x7FFFFFFF: process virtual addresses (accessible to user processes, translated by the kernel, 2GB)
    2. 0x80000000 to 0x9FFFFFFF: kernel direct-mapped addresses (only accessible to the kernel, translated by subtracting 0x80000000, 512 MB cached)
    3. 0xA0000000 to 0xBFFFFFFF: kernel direct-mapped addresses (only accessible to the kernel, 512 MB uncached)
    4. 0xC0000000 to 0xFFFFFFFF: kernel virtual addresses (only accessible to the kernel, translated by the kernel, 1GB)
