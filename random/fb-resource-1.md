# Source

This document covers the questions here:

https://syedali.net/engineer-interview-questions/

# Unix Processes

## What is the difference between a process and a thread?

- A process:
    * Created by the operating system
    * Requires overhead
    * Contains information about program resources and execution state
        + PID, UID, GID
        + Environment
        + Working directory
        + Program instructions
        + Registers, stack, heap
        + File descriptors
        + Signal actions
        + Shared libraries
        + Interprocess communication tools
- A thread:
    * Exists within a process and uses the process resources.
    * Has its own flow of control as long as its parent process exists.
    * May share process resources with threads that act equally independently.
    * Dies if the parent process dies.
    * Is lightweight because overhead has already been accomplished by creation of its process.
- Since threads within the same process share resources:
    * Changes made by one thread to a shared system resource will be seen by others.
    * Two pointers with same value point to the same data.
    * Reading and writing to same memory location is possible.

## What is a Zombie process?

- A zombie process has completed but it is still in the process table waiting for its parent to read its exit status.
- Parent processes normally issue the `wait` system call to read the child's exit status upon which the zombie is removed (reaped).
- `kill` does not work on zombie processes.
- When a child dies, the parent receives a `SIGCHLD` signal.

## How to daemonize a process?

- `fork()` system call to create a separate process.
- `setsid()` system call to detach process from the parent (normally a shell).
- Standard files (stdin, stdout, stderr) need to be reopened.

## Describe ways of inter-process communication.

- Message queues
    * Linked list of messages stored within the kernel.
    * To create a new queue use `msgget()` system call.
    * To add a message to end of queue use `msgsnd()`.
    * To receive a message use `msgrcv()`.
    * Processes must share a common key to access the queue.
- Shared memory
    * Multiple processes given access to same memory block creating a shared bugger for processes to communicate.
    * `shm_open()` creates a new shared memory object.
    * `ftruncate()` allocates some number of bytes to object.
    * `mmap()` get a pointer to the shared memory
    * Writer creates a semaphore with `sem_open()` to ensure exclusive access to the shared memory.
    * Otherwise a race condition would occur if writer was writing and reader was reading at the same time.
    * `sem_post()` releases lock so reader can read.
    * `munmap()` to unmap shared memory from address space.
- Anonymous pipes
    * Has a write end and a read end for FIFO order.
    * One process writes to the pipe and another one reads.
    * Example: `sleep 5 | echo "hello"`
- Named pipes
    * Processes write to and read from a named pipe as if it were a regular file.
    * This is unlike anonymous pipes which use stdin and stdout.
- Domain sockets
    * Enable channel-based communication for process on the same host.
    * Note: This is different from a network socket which allows communication across hosts which need support from an underlying protocol (e.g., TCP or UDP).
    * ICP sockets rely on local system kernel to support communication.
    * ICP sockets use a local file as a socket address.
    * Sockets configured as streams are bidrectional and control follows a client/server pattern.
    * Server steps:
        1. `socket()` to get a file descriptor for the socket connection
        2. `bind()` to bind the socket to an address on the host
        3. `listen()` to listen for client requests
        4. `accept()` to accept a particular client request

## Describe how processes execute in a Unix shell.

- When you run a program e.g., `ls` in the shell, the shell first searches its `path` for an executable named `ls`.
- Typically this is located in `/bin/ls`.
- The shell will call `fork()` to create a copy of itself.
- If `fork()` succeeds, the child shell process will run `exec /bin/ls` which will replace the copy of the child shell with itself.
- Any parameters passed to `ls` are handled by `exec`.
- Note that `exec()` is also a system call.

## What are Unix signals?

- Signals are an IPC method.
- Default `kill` signal is `SIG-TERM` (15).
- `SIG-KILL` (9) cannot be handled by a process and causes it to be forecefully killed.
- Use `kill()` system call to send signals to a process.
- `SIG-HUP` (1) is used to reset or hang up processes when its controlling terminal is closed.
- `SIG-STOP` (17) also cannot be handled by a process. It pauses the process in its current state and waits for `SIG-CONT` to resume.
- Note: `raise()` system call can be used to send a signal to a thread.

## When you send a HUP signal to a process, you notice it has no impact, why?

- Some processes setup signal blocking during critical section execution.
- This is done by using `sigprocmask()` system call to mask certain signals.
- It is possible process was masking `SIG-HUP`.
- It will be handled once the signal is unblocked from the pending.