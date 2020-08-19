# Lecture 3: OS Structures

## System Calls

- Programming interface to services provided by OS
- Typically written in high-level language e.g., C/C++
- Mostly accessed by programs via a high-level API rather than direct system call
- Three most common APIs are POSIX API for POSIX-based systems (Linux, MacOS), and Java API for JVM
- Why use APIs rather than system calls directly?
  * Portability: APIs handle different underlying machines which may expect different system call APIs
  * Example: Standard C Library
    + C program invoking `printf()` library call (user mode) which calls `write()` system call (kernel mode)
    * Switch from user to kernel mode performed after trap is raised to jump into kernel mode
- Typically, a number is associated with each system call
  * System call interface maintains a table indexed according to these numbers
- The system call itnerface invokes intended system call in OS kernel and returns status of the system call and any return values
- Caller needs to know nothing about how the system call is implemented
  * Just needs to obet API and understand what OS will do as a result call
  * Most details of OS interface hidden from programmer by API
- To pass values into system calls, you can:
  1. Pass via registers (in some cases there may be more parameters than available registers)
  2. Store parameters in a block (i.e., table) in memory and address of block passed as a parameter in a register (Linux approach)
  3. Parameters placed or pushed onto a stack by the program and popped off the stack by the OS
  * Last two methods do not limit the number or length of parameters being passed
- More sample system calls:
  * Process management:
    + `fork()`, `exit()`, `wait()`
  * File manipulation:
    + `open()`, `read()`, `write()`, `close()`
  * Device manipulation:
    + `ioctl()`, `read()`, `write()`
  * Information maintenance:
    + `getpid()`, `alarm()`, `sleep()`
  * Communication:
    + `pipe()`, `shmget()`, `nmap()`
  * Protection:
    + `chmod()`, `umask()`, `chown()`

## Basic OS Structure

- Monolithic OS design
  1. Users
  2. Shells and commands, compilers and interpreters, system libraries
  3. System call interface to the kernel
  4. Kernel (protected part of OS that runs in kernel mode protecting critical OS data and device registers from user programs)
    * Signals, file system, CPU scheduling, memory management, etc
  5. Kernel interface to hardware
  6. Terminal controlers (terminals), device controllers (disks), memory controllers (physical memory)
- Layered OS design
  1. User
  2. Device drivers
  3. Virtual memory
  4. I/O channel
  5. CPU scheduler
  6. Hardware
  * Every layer only communicates with layer above and below it
  * Advantages: modularity, simplicity, portability, ease of design/debugging
  * Disadvantages: adds overhead for communication between non-sequenced components
- Microkernel design
  1. User processes running in user mode
  2. System processes (file system , high-level scheduling, thread system, external paging, network support) running in user mode
  3. Micokernel (Low-level VM, protection, communication, processor control) running in kernel mode
  4. Hardware
  * Small kernel that provides communication and other basic functionality
  * Other OS functionalities implemented as user-space processes
  * Advantages: better reliability, easier extension and customization
  * Disadvantages: very high overhead to constantly switch into and out of kernel between system processes
- Hybrid design
  1. Application environments and common services
  2. Kernel environment made of both BSD (monolithic) and Mach (microkernel)
  * Mach microkernel (mem, RPC, IPC)
  * BSD (threads, CLI, networking, filesystem)
  * User services (GUI)

## Modules

- Most OS implement kernel modules
  * Use object-oriented approach
  * Each core component is separate
  * Each talks to the others over known interfaces
  * Each is loadable as needed within the kernel
- Overall, similar to layers but more flexible
- Example: Solaris modular approach
  * Core kernel surrounded by:
    1. Device and bus drivers
    2. Scheduling classes
    3. File systems
    4. STREAMS modules
    5. Loadable system calls
    6. Executable formats
    7. Miscellaneous modules
  * Disadvantages: no protection against malicious kernel modules
