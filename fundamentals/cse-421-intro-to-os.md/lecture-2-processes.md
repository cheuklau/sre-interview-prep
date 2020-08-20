# Lecture 2

## Operating System Abstractions

- Abstractions simplify application design by:
    1. Hiding undesirable properties
    2. Adding new capabilityes
    3. Organizing information
- Abstractions provide an interface to application programmers that separates
    * Policy (what interface commits to accomplishing) from
    * Mechanism (how the interface is implemented)

## Example Abstraction: File

- What undesirable properties do files hide:
    * Disks are slow
    * Chunks of storage are distributed over the disk
    * Disk storage may fail
- What capabilities do files add:
    * Growth and shrinking
    * Organization into directories
- What information do files help organize:
    * Ownership and permissions

## Preview of Coming Abstractions

- Thread map to CPU
- Address space map to memory
- File map to disk

## The Process

- Processes are the most fundamental OS abstractions
- Unlike threads, address spaces and files, processes are not tied to a hardware component
- Instead processes contain other abstractions:
    * One or more threads
    * Address space
- OS is responsible for isolating processes from each other
    * What you do in your own process is your own business but it shouldn't be able to crash the machine or affect other processes
    * Therefore, safe intra-process communication is your problem
    * Safe inter-process communication is an OS problem
- Intra-process communication
    * Communication between multiple threads in a process usually accomplished using shared memory
    * Threads within a process share open file handles and both static and dynamically-allocated global variables
    * Thread stacks and thus thread local variables are typically private
    * Sharing data requires synchronization mechanisms to ensure consistency
- Inter-process communication
    * A variety of mechanisms exist to enable inter-process communication (IPC)
        + Shared files or sockets, exit codes, signals, pipes, shared memory
    * All require coordination between the communicating processes
    * Most have semantics limiting the degree to which processes can interfere with each other
        + A process can't just send a `SIGKILL` to any other process running on the machine
- Return codes is an example of IPC
    * When process `exit` it returns exit code to parent process
    * In Bash run `echo $?` to get return code of previous command
- Pipes
    * `ps aux | grep myprog`
    * Pipes create a producer-consumer buffer between two processes
    * Allows output from one process to be used as the input to another
    * OS manages a queue for each pipe to accomodate different input and output rates
- Signals
    * `kill <pid>`
    * `kill -9 <pid>` sends `SIGKILL` which cannot be ignored by a process
    * `control-c` sends `SIGTERM` which processes can ignore
    * Signals are a limited form of asynchronous communication between processes
    * Processes can register a signal handler to run when a signal is received
    * Users can send signals to processes owned by them
    * Super-user can send a signal to any process
    * Processes can ignore most signals except `SIGKILL` (non-graceful termination)

## Processes vs. Threads

- Note: We can describe both a process and a thread as running
    * Most apps are multi-thread
    * A process requires multiple resources: CPU, memory, files, etc
    * A thread of execution abstracts CPU state
- Processes contain threads and threads belong to a process
    * Only one exception: kernel may have threads of execution not associated with any user process
    * Note: Except the kernel process which is a process
- A process is considered to be running when one or more of its threads are running

## Process Example: Firefox

- Firefox has multiple threads. What are they doing?
    * Waiting for and processing interface events e.g., mouse clicks, keyboard input, etc
    * Redrawing the screen as necessary in response to user input, web page loading, etc
    * Loading web pages - usually multiple parts in parallel to speed things up
- Firefox is using memory. For what?
    * `Firefox.exe` i.e., the executable code of Firefox itself
    * Shared libraries for web page parsing, security, etc
    * Stacks storing local variables for running threads
    * A heap storing dynamically-allocated memory
- Firefox has files open. Why?
    * Configuration files
    * Fonts