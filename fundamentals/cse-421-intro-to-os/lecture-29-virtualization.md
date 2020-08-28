# Lecture 29

## What is Virtualization?

- Until we've been talking about OS running on physical machines: a collection of:
    1. Real hardware resources
    2. That the OS has exclusive access to
    3. Through hardware interfaces (instruction set architectures, device I/O ports, etc)
- OS can also run inside VMs implemented by virtual machine monitors (VMMs)
    * We refer to an OS running inside a VM as a guest OS
- Virtual machines differ from physical machines in important ways
    * They do not provide the guest OS with exclusive access to underlying physical machine
    * Equivalently they do not provide the guest OS with privileged access to the physical machine
- The virtual machine monitor (VMM) is
    1. A piece of software running on an OS (host OS)
    2. That can allow another OS (the guest OS) to be run as an application
    3. Alongside other applications
    * When we said that the OS was really just another program, we weren't kidding

## Problems with OS: Hardware Coupling

- Unfortunate coupling between hardware resources and the OS
    1. Hard to run multiple OS on the same machine
    2. Difficulat to transfer software setups to another machine, unless it has identical or nearly identical hardware
    3. Messy to adjust hardware resources to system needs; requires sticking your hand in the box and mucking around
    4. Requires static, up-front provision of machine resources

## Problems with OS: Application Isolation

- Lack of true isolation between multiple applications
    1. OS leak a lot of information between processes through the file system and other channels
    2. Multiple applications may require specific and conflicting software packages to run
    3. Certain applications may have very specific OS configuration and tuning requirements
    4. In some cases, software vendors will not provide support if you are running the applications alongside anything else

## Why We Virtualize

- We can package and distribute an entire software development environment which can be used and discarded
- We can dynamically divide up one large machine into multiple smaller machines, each running a different OS and applications
- We can easily replicate an entire machine image in order to duplicate or move it

## To Be a VMM

- Three essential requirements for a piece of software to be considered a VMM:
    1. Fidelity: software on the VMM executes identically to how it would on real hardware
    2. Performance: to achieve good performance most instructions executed by guest OS should be run directly on the underlying physical hardware
    3. Safety: VMM should manage all hardware resources

## Three Approaches to Virtualization

1. Full virtualization
    * Should be able to run an unmodified guest OS
    * Example: VirtualBox
2. Paravirtualization
    * Includes small changes to the guest OS to improve interaction with the virtual machine monitor
    * Example: Xen, Amazon EC2
3. Container virtualization
    * Namespace and other isolation techniques performed by the OS to isolate sets of applications from each other
    * Example: Docker

## Full Virtualization

- Our goal: run an unmodified OS and apps in a VM itself running on a host OS and potentially next to other VMs
- Why is this hard?
    * How do we handle traps by applications running in the guest OS?
    * Guest OS will try to execute privileged instrcutions

## De-Privileging the Guest OS

- What happens if we run the guest OS with kernel privileges
    * Privileged instructions work as expected but guest has access to the entire machine
- What happens if we run the guest OS with user privileges
    * Need to figure out how to deal with privileged instructions

## Trapping Privileged Instructions

- Ideally, when privileged instructions are run by the guest OS at user privilege level:
    1. The CPU traps the instruction due to a privilege violation
    2. The trap is handled by the VMM
    3. Assuming the guest OS is doing something legitimate the VMM adjusts the VM state and continues the guest OS
        * We refffer to an instruction set having the property as classically virtualizable
        * We refer to the approach described above as trap and emulate

## Trap and Emulate

- What does the VMM do with traps that occur within the virtual machine
    * If the trap is caused by an application, pass the trap to the guest OS
    * If the trap is caused by the guest OS, handle the trap by adjusting the state of the virtual machine

## Getting Trappy

- VMWare and VirtualBox VMMs run as standard system processes but require OS support
    * All traps and exceptions orgiinating inside the VM must be handled by the VMM
    * Most of the time guest apps and guest OS simply use the physical processor normally
- What happens when an app running inside the virtual machine makes a system call
    1. `syscall`: host OS vectors trap to VMM
    2. VMM inspects trap, identifies it as a system call, and passes control and arguments to guest OS trap handling code
    3. `rfe`: when the guest OS is done, it will also trap back to the VMM by executing a privileged instruction
    4. VMM will pass arguments back to the process that originated the system call
- What happens when a process inside the virtual machine creates a TLB fault?
    1. Trap to the host OS
    2. Hand trap to the VMM
    3. VMM inspects trap, sees it was generated by the app, passes control to the guest OS
    4. Guest OS begins handling the TLB fault, tries to load an entry into the TLB
    5. Trap to the host OS
    6. Hand trap to the VMM
    7. VMM inspects trap, sees that it was generated by the guest OS, adjusts the state of the virtual machine appropriately

## Hardware Virtualization

- Note that what is being virtualized is the hardware interface
- Lets compare to virtual memory
    * What is the interface?
        + Load and store
    * How do we ensure safety?
        + Translate every unprivileged memory access
    * How do we get good performance?
        + Cache translations in the TLB
- What about full hardware virtualization
    * What is the interface?
        + All instructions executed on the processor that modify the state of the machine
    * How do we ensure safety?
        + Intercept or rewrite unsafe instructions that could pierce the VM
    * How do we get good performance?
        + Allow safe instructions to run directly on the physical hardware (on bare metal)

## Sadly

- The x86 architecture is not classically virtualizable
    * Some instructions did not trap correctly
    * Others had different side effects when run in kernel or user mode
- VMWare developed an innovative solution to this problem: binary translation
    * During guest OS execution scan code pages for non-virtualizable instructions and rewrite them to safe instruction sequences
    * Cache translations to improve performance