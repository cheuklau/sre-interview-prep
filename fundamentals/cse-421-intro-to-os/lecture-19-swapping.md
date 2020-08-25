# Lecture 19

## Out of Core

- When we run out there are two options:
    1. Fail, and either don't load process `exec()`, create a new process `fork()`, refuse to allocate more memory `sbrk()` or kill process if it is trying to allocate more stack
    2. Create more space, preserving contents of memory for future use
- Virtual address translation gives kernel ability to remove memory from a process behind its back
    * Requirements for doing this:
        * Last time process used virtual address it behaved like memory
        * Next time process uses the virtual address it behaves like emmory
        * In between, whatever data was stored at that address must be preserved

## Swapping

- The place OS typically place data store in memory in order to borrow the memory from the process is on disk
- We call the process of moving data back and forth from memory to disk in order to improve memory usage swapping
- Goal: when swapping is done well, your system feels like it has memory that is as large as the size of the disk but fast as actual RAM
- Unfortunately, when swapping is not done well, your system feels like it has memory that is as small as RAM and as slow as disk

## TLB vs. Page Fauls

- We distinguish between two kinds of memory-related fault:
    1. TLB fault: required virtual to physical address translation not in TLB
    2. Page fault: contents of a virtual page are either not initialized or in memory
- Every page fault is preceded by a TLB fault
    * If the contents of the virtual page are not in memory, a translation cannot exist for it
- Not every TLB fault generates a page fault
    * If page is in memory and the translation is the page table, the TLB fault can be handled without generating a page fault

## Swap Out

- To swap a page to disk we must:
    1. Remove the translation from the TLB, if it exists
    2. Copy the contents of the page to disk
    3. Update page table entry to indicate that the page is on disk
- Note: If process tries to access same virtual address, TLB will not have it so process will sleep until swap in is done

## Swap Out Speed

- Remove translation from TLB: fast
- Copy contents of page to disk: slow
- Update the page table entry to indicate that page is on disk: fast

## Page Cleaning

- Frequently when we are swapping out a page it is in order to allocate new memory to a running process or possibly to swap in a page
- So it would be great if swapping out were fast
- Can we prepare the system to optimize swap out? Yes
    * Each page has a dedicated place on disk
    * During idle periods, OS writes data from active memory pages to swap disk
    * Pages with matching content on the swap disk are called clean
    * Pages that do not match their swap disk content are called dirty

## Swap In

- When must we swap in a page?
    * When the virtual address is used by the process
- To translate a virtual address used by a process that points to a page that has been swapped out, we must:
    1. Stop the instruction that is trying to translate the address until we can retrieve the contents
    2. Allocate a page in memory to hold the new page contents
    3. Locate the page on disk using the page table entry
    4. Copy the contents of the page from disk
    5. Update the page table entry to indicate that the page is in memory
    6. Load the TLB
    7. Restart the instruction that was addressing the virtual address we retrieved
- Note: thrashing refers to programs continuously trigger page faults, swapping pages in and out, OOM killer starts killing processes

## On-Demand Paging

- Sometimes procastination is useful particularly when you end up never having to do the thing you're being asked to do
- Process: kernel, load this huge chunk of code into my address space
- Kernel: I am busy, but I will make a note of it
- Process: kernel, give me 4MB more heap
- Kernel: request is granted, but come back when you really need it
- Until an instruction on a code page is executed or a read or write occurs to a data or heap page, the kernel does not load the contents of that page into memory
- Why not?
    * A lot of code is never executed and some global variables are never used. Why waste memory?

## Demanded Paging

- What happens the first time a process executes an instruction from a new code page?
    * That page contents are loaded from disk and the instruction is started
- What happens the first time a process does a load or store to an uninitialized heap, stack or data page?
    * The kernel allocates a new page filled with zeros and the instruction is restarted

## Aside: Hardware-Managed TLBs

- On certain architectures, the MMU will search the page table itself to locate virtual-to-physical address translations missing from the TLB
    * Pro: Hardware is faster
    * Con: OS must set up page tables in a fixed way that the hardware understands
- With hardware-managed TLB, kernel never sees TLB faults (handled in the hardware)
