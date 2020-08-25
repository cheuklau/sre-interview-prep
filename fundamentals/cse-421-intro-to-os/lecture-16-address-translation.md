# Lecture 16

## Translation is Control

- Forcing processes to translate a reference to gain access to the underlying object proides the kernel with a great deal of control
- References can be revoked, shared, moved, altered

## Virtual vs. Physical Memory

- Address space abstraction requires breaking connection between a memory address and physical memory
- We refer to data accessed via memory interface as using virtual addresses
- Physical address points to memory
- Virtual address points to something that acts like memory
- Virtual addresses have much richer semantics than physical addresses, encapsulating location, permanence and protection

## Creating Virtual Addresses

- `exec()` creates virtual addresses using ELF file as a blueprint
- `fork()` copies virtual address space of parent process
- `sbrk()` extends the process heap e.g., by `malloc()`
- `mmap()` creates a virtual address region that points to a file

## Efficient Translation

- Goal: almost every virtual address translation should be able to proceed without kernel assistance
- Why:
    * Kernel is too slow
    * Recall: kernel sets policy, hardware provides the mechanism

## Explicit Translation

- Process: "Dear kernel, I would like to use virual address 0x10000, please tell me what physical address this maps to?"
- Does this work?
    * No, it is unsafe. We can't allow process to use physical addresses directly. All addresses must be translated.

## Implicit Translation

- Process: "Machine, store to address 0x10000"
- MMU: "Where does virtual address 0x10000 supposed to map to? Kernel, help!"
- Exception
- Kernel: "Machine, virtual address 0x10000 maps to physical address 0x567400"
- MMU: "Process, store completed"
- Note: if not translatable then we get a segmentation fault

## K.I.S.S Base and Bound

- Simplest virtual address mapping approach:
    1. Assign each process a base physical address and bound
    2. Check: virtual address is okay if virtual address is less than bound
    3. Translate: physical address = virtual address + base
        * Example:
            + Virtual address = 0x100000
            + Base = 0x40600, Bounds = 0x30000
            + Physical memory = virtual address + base = 0x50600
            + Note: if physical memory > bounds then process will fail (translation fails)

## Base and Bounds: Pro

- Pro: simple, hardware only needs to know base and bounds
- Pro: fast
    * Protection: one comparison
    * Translation: one addition

## Base and Bounds: Con

- Con: this is not a good fit for our address space abstraction
    * Address spaces encourage discontiguous allocation
    * Base and bounds allocation must be mostly contiguous otherwise we lose memory to internal fragmentation
- Con: also signficant chance of external fragmentation due to large contiguous allocations

## Segmentation

- One base and bounds isn't a good fit for address space abstraction
- We can extend this idea
    * Multiple bases and bounds per process (call each a segment)
    * Assign each logical region of the address space (code, data, heap, stack) to its own segment
        + Each can be separate size
        + Each can have separate permissions
- Segmentation works as follows:
    1. Each segment has a start virtual address, base physical address and bound
    2. Check: virtual address is aokay if it is inside some segment or for some segment:
        + segment start < virtual address < segment start + segment bound
    3. Translate: for the segment that contains htis virtual address:
        + physical address = virtual address - segment start + segment base
- Example:
    * 0x10000 virtual memory
    * MMMU asks kernel if valid segment exists, and kernel replies with
        + start 0x100000, base 0x43000, bounds 0x1000
    * Mapped to physical address 0x43000
- Example:
    * 0x400 virtual memory
    * MMU asks kernel if valid segment exists, and kernel replies with
        + start 0x100, base 0x16000, bounds 0x500
    * Mapped to physical 0x16300
- Segmentation fault, core dumped mean you tried to access invalid virtual memory

## Segmentation: Pros

- Still fairly simple
    * Protection (segment exists): N comparisons for N segments
    * Translation: one addition
- Can organize and protect regions of memory appropriately
- Better fit for address spaces leading to less internal fragmentation

## Segmentation: Cons

- Still requires entire segment to be contiguous in memory
- Potential for external fragmentation due to segment contiguity

## Ideal

- Ideally, we would like:
    * Fast mapping from any virtual byte to any physical byte
    * OS cannot do this. Can hardware help?

## Translation Lookaside Buffer

- Common system trick: when something is slow, throw a cache at it
- Translation Lookaside Buffer (TLB) typically use content-addressable memory or CAMs to quickly search for a cached virtual-physical translation
- Example:
    * TLB contains virtual to physical mapping:
        + 0x10 to 0x50
        + 0x800 to 0x306
        + 0x110 to 0x354
    * CAMs can search a large number of mapping e.g., 256 at once turning O(n) search operation to O(1)

## TLB Cons

- CAMs are limited in size, cannot be arbitrarily large
- Segments are too large and lead to internal fragmentation
- Mapping individual bytes would nmean that the TLB would not be able to cache many entries and eprformance would suffer
- Is there a middle ground? Yes: page translation and page management