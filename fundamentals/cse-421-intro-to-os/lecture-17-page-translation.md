# Lecture 17

## Pages

- Modern solution is to choose a translation granularity that is small enough to limit internal fragmentation but large enough to allow TLB to cache entries covering a significant amount of memory
    * Also limits the size of kernel data structures associated with memory management
- Execution locality also helps here: process memory accesses are typically highly spatially clustered meaning that even a small cache can be effective

## Page Size

- 4K is a very common page size
- 8K or larger pages are also sometimes used
- 4K pages and a 128-entry TLB allow caching translations for 1 MB of memory
- You can think of pages as fixed size segments so the bound is the same for each

## Page Translation

- We refer to the portion of the virtual address that identifies the page as the virtual page number (VPN) and the remainder as the offset
- Virtual pages map to physical pages
- All addresses inside a single virtual page map to the same physical page
- Check: for 4K pages, split 32-bit address into virtual page number (top 20 bits) and offset (bottom 12 bits); check if a virtual page to physical page translation exists for this page
- Translate: physical address = physical page + offset

## TLB Example

- Assume we have a TLB:
    * 0x10 to 0x50
    * 0x800 to 0x306
    * 0x110 to 0x354
    * 0x674 to 0x232
- For 0x800346 virtual address we split it to 0x800 and 346 where 346 is the offset
- 0x800 maps to 0x306 physical page number
- We combine the physical page number and the offset to get the physical address of 0x306346

## TLB Management

- Where do entries in the TLB come from?
    * The OS loads them
- What happens if a process tries to access an address not in the TLB?
    * TLB asks OS for help via a TLB exception
    * OS either load the mapping or figure out what to do with the process (possibly termination)

## Paging Pros

- Maintains many of the pros of segmentation, which can be layered on top of paging
- Can organize and protect regions of memory appropriately
- Better fit for address spaces
    * Even less internal fragmentation than segmentation due to smaller allocation size

## Paging Cons

- Requires per-page hardware translation: use hardware to help us
- Requires per-page OS state: a lot of clever engineering here

## Page State

- In order to keep the TLB up-to-date we need to be able to:
    * Store info about each virtual page
    * Locate that information quickly

## Page Table Entries (PTEs)

- We refer to a single entry storing information abou ta  single virtual page used by a single process as a page table entry (PTE)
    * Can usually jam everything into one 32-bit machine word:
        + Location: 20 bits (physical page number or location on disk)
        + Permissions: 3 bits (read, write, execute)
        + Valid: 1 bit (is the page located in memory)
        + Referenced: 1 bit (has the page been read/written to recently)

## Locating Page State

- Process: "Machine, store to address 0x10000"
- MMU: "Where is the virtual address 0x10000" supposed to be? Kernel, help!"
- Exception
- Kernel: "Let's see where did put that page table entry for 0x10000. I should be more organized!"
- What are some requirements for how we locate page information:
    * Speed: translation is a hot path and should be efficient as possible
- Data structure used to quickly map a virtual page number to a page table entry is called a page table