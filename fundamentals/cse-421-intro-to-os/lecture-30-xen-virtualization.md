# Lecture 30

## Paper Overview

- What is the wrong way
    * Full virtualization
        + There are situations in which it is desirable for the hosted OS to see real as well as virtual resources
        + Providing both real and virtual time allows a guest OS to better support time-sensitive tasks and to correctly handle TCP timeouts and RTT estimates
        + Exposing real machine addresses allow a guest OS to improve performance by using superpages or page coloring
- So what is the big idea?
    * Paravirtualization
        + Trade off small changes to the guest OS for big improvements in performance and VMM simplicity
        + Present a virtual machine abstraction that is similar but not identical to underlying hardware
        + Promises improved performance although it does require modifications to the guest OS
        + Does not require changes to the application binary interface (ABI) and hence no modifcations required to guest applications

## Xen Design Principles

1. Support for unmodified application binaries is essential
    * Must virtualize all architectural features required by existing standard ABIs
2. Supporting full multi-application OS is important allowing complex server configurations to be virtualized within a single guest OS instance
3. Paravirtualization is necessary to obtain high performance and strong resource isolation on uncooperative machine architectures such as x86
4. Even on cooperative machine architectures, completely hiding the effects of resource virtualization from guest OSes risks both correctness and performance
- Xen introduces the idea of a hypervisor, a small piece of control software similar to the VMM running below all OSes running on the machine
- Much of the typical VMM functionality is moved to the control plane software that runs inside a Xen guest

## Summary of Xen Changes

- Memory management
    * Segmentation: cannot install fully-privileged segment descriptors and cannot overlap with top end of the linear address space
    * Paging: guest OS has direct read access to hardware page tables but updates are hatched and validated by the hypervisor
- CPU
    * Protection: guest OS must run at a lower privilege level than Xen
    * Exceptions: guest OS must register a descriptor table for exception handlers with Xen; aside from page faults, the handlers remain the same
    * System calls: Guest OS may install a fast handler for system calls allowing direct calls from an application into its guest OS and avoiding indirecting through Xen on every call
    * Interrupts: hardware interrupts are replaced with a lightweight event system
    * Time: each guest OS has a timer interface and is aware of both real and virtual time
- Device I/O
    * Network, disk, etc: virtual devices are elegant and simple to access; data is transferred using asynchronous I/O rings; an event mechanism replaces hardware interrupts for notfications

## Virtual Machine Memory Interface

- Virtualizing memory is hard, but its easier if the architecture has
    * A software-managed TLB which can be efficiently virtualized or
    * A TLB with address space identifiers which does not need to be flushed on every transition
- Of course the x86 has neither of these features
    * Given these limitations, we:
        1. guest OSes are responsible for allocating and managing hardware page tables with minimal involvement from Xen to ensure safety and isolation
        2. Xen exists in a 64MB section at the top of eery address space, thus avoiding a TLB flush when evetering and leaving the hypervisor
- But how then do we ensure safety?
    * Each time a guest OS requires a new page table, perhaps because a new process is beign created, it allocates and initializes a page from its own memory reservation and registers it with Xen
    * At this point, the OS must relinquish direct write privileges to the page table memory: all subsequent updates must be validated by Xen
    * Guest OSes may batch update requests to amortize the overhead of entering the hypervisor
    * Top 64MB region of each address space, which is reserved for Xen is not accessible or remapped by guest OSes
    * This address region is not used by any of the common x86 ABIs however so this restriction does not break application compatibility

## Virtual Machine CPU Interface

- Principally the insertion of a hypervisor below the OS violates the usual assumption that OS is most privileged entity in the system
- To protect hypervisor from OS misbehavior guest OSes must be modified to run at a lower privilege level
    * x86 privilege rings to the rescue
    * Rings 1 and 2 have not been used by any well known x86 OS since OS/2
- What exceptions happen enough to create a performance problem? Page faults and system calls
    * Typically only two types of exceptions occur frequently enough to affect system performance: system calls and page faults
    * We improve the performance of system calls by allowing each guest OS to register a fast exception handler which is accessed directly by the processor without indirecting via ring 0
    * This handler is validated befor einstalling it in the hardware exception table

## Para vs Full Virtualization

- Full virtualization: do not change the OS except at run time
- Paravirtualization: minimial changes to the OS which sometimes results in better interaction between the OS and virtual hardware