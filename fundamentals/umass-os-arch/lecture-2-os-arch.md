# Lecture 2: OS and Architecture

## Modern OS Overview

- Modern OS functionality:
    * Process and thread management
    * Concurrency
        + Doing many things simultaneously (I/O, processing, multiple programs, etc)
        + Several users work at the same time
        + Threads (unit of OS control); one thread on the CPU at a time, but many threads active concurrently
    * I/O devices
        + Let CPU work while a slow I/O device is working
    * Memory management
        + OS coordinates memory allocation and moving data between disk and main memory
    * Files
        + OS coordinates how disk space is used for files in order to find files and to store multiple files
    * Distributed systems and networks
        + Allow a group of machines to work together on distributed hardware

## Computer Architecture Basics

- CPU
    * Processoor that performs actual computation
    * Multiple cores common in today's processors
- I/O devices
    * Terminal, disks, videoo board, printer, etc
    * Network card
- Memory
    * RAM containing data and proograms used by the CPU
- System bus
    * Communication medium between CPU, memory, and peripherals

## Architectural Features Motivated by OS Services

- Protection
    * Kernel/user mode, protected instructions. base/limit registers
- Interrupts
    * Interrupt vectors
- System calls
    * Trap instructions and trap vectors
- I/O
    * Interrupts and memory mapping
- Scheduling, error recovery and accounting
    * Timer
- Synchronization
    * Atomic instructions
- Virtual memory
    * Translatin look-aside buffers

### Protection

- CPU supports a set of assembly instructions
    * `MOV [address], ax`
    * `ADD ax, bx`
    * `MOV Crn` (move control register)
    * `IN. INS` (input string)
    * `HLT` (halt)
    * `LTR` (load task register)
    * `INTn` (software interrupt)
- Some instructions are sensitive or privileged e.g., `HLT`
- Kernel vs user mode
    * To protect system from bad users and processors, some instructions are restricted to use only by the OS
    * Users may not:
        + Address I/O directly
        + Use instructions that manipulate the state of memory
        + Set the mode bits that determine user or kernel mode
        + Disable and enable interrupts
        + Halt the machine
    * In kernel mode, the OS can do the above things
- Hardware must support at least kernel and user mode
    * Status bit in a protected processor register indicates the mode
    * Protected instructions can only be executed in kernel mode

### System Calls

- System call
    * OS procedure that executes privileged instructions (API exported by the kernel)
    * Causes a trap which vectors (jumps) to the trap handler in the OS kernel
    * Trap handler uses the parameter to the system call to jump to the appropriate handler (e.g., I/O, terminal, etc)
    * Handler saves caller's state so it can restore control to the user process
    * Architecture must permit OS to verify the caller's parameters
    * Architecture must also provide a way to return to user mode when finished
- Example system calls for process management
    * `pid=fork()`: creates a child proocess identical to the parent
    * `pid=waitpid(pid,&statloc,optins)`: wait for a child t oterminate
    * `s=execve(name,argc,environp)`: replace a process' core image
    * `exit(status)`: terminate process execution and return status
- Example system calls for file management
    * `fd=open(file,how,...)`: open a file for reading, writing or both
    * `s=close(fd)`: close an open file
    * `n=read(fd,buffer,nbytes)`: read data from a file into a buffer
    * `n=write(fd,buffer,nbytes)`: write data from a buffer into a file
    * `position=lseek(fd,offset,whence)`: move file pointer
    * `s=stat(name,&buf)`: get file's status information
- Others: `stat`, `mkdir`, `link`, `mount`, `chdir`, `chmod`, `kill`, `time`

### Memory Protection

- Architecture must provide support so OS can:
    * Protect user programs from each other
    * Protect OS from user programs
- Simplest technique is to use base and limit registers
- Base (where valid memory address starts) and limit (where valid memory address ends) registers are loaded by the OS before starting a program
- CPU checks each reference (instruction and data addresses), ensuring it falls between the base and limit register values

### Process Layout in Memory

- Process address space divided into:
    * Stack `FFFF`: As program runs it pushes operands onto the stack and pops return values from the stack
    * Gap
    * Data: Statically allocate memory for objects onto the heap
    * Text `0000`: Actual code of the program that is running (static)

### Registers

- Register: basic unit of memory (word) managed by the CPU
    * General purpose: `AX`, `BX`, `CX` on x86
    * Special purpose:
        + `SP` = stack pointer
        + `FP` = frame pointer
        + `PC` = program counter
            - Indicates current and next instruction
- Change processes
    * Save current registers
    * Load saved registers
    * Above results in a context switch

### Memory Hierarchy

- From fastest to slowest, and smallest to largest:
    1. Registers (1-cycle latency, 1 kB)
    2. L1 (2-cycle latency, 10s of kB)
    3. L2 (7-cycle latency, couple MBs)
    4. RAM (100-cycle latency, tens of GBs)
    5. Disk (40,000,000-cycle latency)
    6. Network (200,000,000-cycle latency)
- L1 and L2 managed by architecture, not OS

### Caches

- Access to main memory expensive
- Caches: small, fast, expensive memory
    * Hold recently-accessed data `D$` or instructions `I$`
    * Different sizes and locatioons
        + L1 - On-chip (tens of kB)
        + L2 - on or next to chip (a few MB)
        + L3 - on bus (several MB)
    * Manages lines of memory (32-128 bytes)
    * Caches are managed by hardware (no explicit OS management)

### Traps

- Traps: special conditions detected by architecture
    * Examples: page fault, write to a read-only page, overflow, system calls
- On detecting a trap, the hardware:
    * Saves the state of the process (PC, stack, etc)
    * Transfers control to the appropriate trap handler (OS routine that knows what to do with the trap)
        + CPU indexes the memory-mapped trap vector (list of memory addresses that tells where each piece of code are to handle each trap) with the trap number
        + Jumps to the address given in the vector
        + Starts to execute at that address
        + On completion, OS resumes execution of the process
- Example trap vector:
    * `0: 0x00080000` for illegal address
    * `1: 0x00100000` for memory violation
    * `2: 0x00100480` for illegal instruction
    * `3: 0x00123010` for system call
- Modern OS use virtual memory traps for debugging, distributed VM, garbage collection, etc
- Traps are a performance optimization
    * Less efficient solution is to insert extra instructions into the code everywhere a special condition could arise

### I/O Control

- Each I/O device has a little processor inside it that enables it to run autonomously
- CPU issues commands to I/O devices and continues
- When I/O device completes the command, it issues an interrupt
- CPU stops whatever it was doing and the OS processes the I/O devices interrupt
- Three I/O methods:
    1. Synchronous (blocking I/O)
        * Process issues request and waits for I/O request to complete
        * Not necessarily the most efficient for your program, but other processes can be run while it waits for I/O request to complete
    2. Asynchronous (non-blocking I/O)
        * Process issues request through the request driver
        * Device driver starts processing
        * Requesting process returns control immediately, not waiting for I/O to complete
        * Sometime later hardware finishes processing I/O request
        * Returns data to the device driver
        * Interrupt is sent which goes back to requesting process
        * Process retrieves data
    3. Memory-mapped
        * Enables direct access to I/O controller (vs. being required to move the I/O code and data into memory)
        * PCs reserve a part of physical memory and put device manager in that memory e.g., all bits for a video frame for a video controller
        * Access to the device then becomes almost as fast and convenient as writing the data directly into memory
        * Efficient for transferring large amounts of data

### Interrupt-Based Asynchronous I/O

- Device controller has its own small processor which executes asynchronously with main CPU
- Device puts an interrupt signal on the bus when finished
- CPU takes an interrupt and performs the following:
    1. Saves critical CPU state (hardware state)
    2. Disables interrupts
    3. Saves state that interrupt handler will modify (software state)
    4. Invokes interrupt handler using the in-memory interrupt vector
    5. Restores software state
    6. Enables interrupts
    7. Restores hardware state, and continue execution of interrupted process

### Timer and Atomic Instructions

- Timer
    * Time of day
    * Accounting and billing
    * CPU protected from being hogged using timer interrupts that occur at say every 100 microseconds
        + At each timer interrupt, CPU chooses a new process to execute
    * Interrupt vector:
        + `0: 0x2ff080000` for keyboard
        + `1: 0x2ff100000` for mouse
        + `2: 0x2ff100480` for timer
        + `3: 0x2ff123010` for disk1

### Synchronization

- Interrupts interfere with executing processes
- OS must be able to synchronize cooperating, concurrent processes
    * Architecture must provide a guarantee that short sequences of instructions (e.g., read-modify write) execute atomically
    * Two solutions:
        1. Architecture mechanism to disable interrupts before sequence, execute sequence, enable interrupts again
        2. A special instruction that executes atomically i.e., it will not be interrupted by anything running on processor

### Virtual Memory

- Allows users to run programs without loading entire program into memory at once
- Pieces of program are loaded as needed
- OS keeps track of which pieces are in physical memory and which pieces are on disk
- Order for pieces of the program to be located and loaded without causing major disruption of program, the hardware provides a translation lookaside buffer (TLD) to speed the lookup