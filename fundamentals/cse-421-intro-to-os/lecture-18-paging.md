# Lecture 18

## Locating Page State

- We want MMU's cache (TLB) to have the address mapping to physical memory
- If MMU does not have it, it asks the kernel which needs an efficient way to look up
- Requirements for how we locate page information:
    * Speed: translation is a hot path and should be as efficient as possible
    * Compactness: data structures we should use should not take up too much physical memory

## Page Tables

- Data structure used to quickly map a virtual page number to a page table entry is called a page table
    * Each process has a separate page table

## Flat Page Tables

- Approach: use one array to hold all page table entries for each process
    * Virtual page number is index into this array
        + Speed: O(1) VPN is used directly as an index into the array
        + Compactness: amount of memory (4MB) per process can have that may have to be contiguous (most is unused)

## Linked List Page Tables

- Approach: List of PTEs for each process, searched on each translation
    * Size: scaled with number of process memory allocates i.e., 4bytes*`n` for `n` valid virtual pages
    * Speed: O(n) for n valid virtual pages

## Multi-Level Page Tables

- Approach
    * Build a tree-like data structure mapping VPN to PTE
    * Break VPN into multiple parts, each used as an index at a separate level of the tree
- Example:
    * With 4K pages VPN is 20 bits
    * Use top 10 bits as index into top-level page table
    * Bottom 10 bits as index into second-level page table
    * Each page table is `2^10 * 4` bytes = 4K
- Speed: O(c): constant number of lookups per translation depending on tree depth
- Compactness: depends on sparsity of address space, but better than flat and worse than linked list

## Out of Core

- So far we have been talking about cases where processes are able to use physical memory available on the machine
- What happens when we run out?
- When we run out there are two options:
    1. Fail: either don't load `exec()`, don't create a new process `fork()`, refuse to allocate more heap `sbrk()`, or kill the process if it is trying to allocate more stack
    2. Create more space, preserving the contents of memory for later use

## Virtually Sneaky

- Virtual address translation gives the kernel the ability to remove memory from a process behind its back
- What are the requirements for doing this?
    * The last time the process used the virtual address, it behaved like memory
    * The next time the process uses the virtual address, it behaves like memory
    * In between, whateveer data was stored at that address must be preserved

## Swapping

- Place OS typically place data stored in memory in order to borrow the memory from the process is on disk
- We call the process of moving data back and forth from memory to disk in order to improve memory usage swapping
- Goal: when swapping is done well you system feels like it has memory that is as large as the size of the disk but as fast as actual RAM
- Unfortunately, when swapping is not done well, your system feels like it has memory that is as small as RAM and as slow as disk