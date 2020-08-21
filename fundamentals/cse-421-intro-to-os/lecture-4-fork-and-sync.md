# Lecture 4

## Pipes

- Chains of communicating processes can be created by exploiting the `pipe()` system call
- Standard output of one process is passed as standard input to another
- `pipe()` creates an anonymous pipe object and returns two file descriptors
    1. For the read-only end
    2. For the write-only end
- Pipe contents are buffered in memory
- IPC using `fork()` and `pipe()`:
    1. Before calling `fork()`, parent creates a pipe object by calling `pipe()`
    2. Next, it calls `fork()`
    3. After `fork()`, the parent closes its copy of the read-only end and the child closes its copy of the write-only end
    4. Now the parent can pass information to its child
- Issues with `fork()`
    * Copying all the state is expensive
        + Especially when the next thing that a process does is starting to load a new binary which destroys most of the state `fork()` has carefully copied
    * Several solutions to this problem:
        + Optimize existing semantics through copy-on-write
        + Change the semanitcs `vfork()` which will fail if the child does anything other than immediately load a new executable
            - Note: this does not copy the address space
    * What if I don't want to copy process state
        + `fork()` is now replaced by `clone()` - a more flexible primitive that enables more control:
            - Over sharing, including sharing memory and signal handlers
            - Over child execution, which begins at a function pointer passed to the system call instead of resuming at the point where `fork()` was called
- `fork()` establishes a parent-child relationship between two processes at the point when one is created
- `pstree` utility allows you to visualize these relationships

## Synchronization

- The OS creates the illusion of concurrency by quickly switching the processors between multiple threads
- Threads are used to abstract and multiplexes the CPU
- The illusion of concurrency is both powerful and useful
    * Helps us think about how to structure our applications
    * Hides latencies caused by slow hardware devices
- Unfortunately, concurrency also creates problems
    * Coordination: how do we enable efficient communication between the multiple threads involved in performing a single task
    * Correctness: how do we ensure shared state remains consistent when being accessed by multiple threads concurrently?
        + How do we enforce time-based semantics

## Patient 0

- The OS itself is one of the most difficult concurrent programs to write
    * It is multiplexing access to hardware resources and therefore sharing a lot of state between multiple processes
    * It is frequently using many threads to hide hardware delays while servicing devices and application requests
    * Lots of shared state plus lots of threads equals a difficult synchronization problem
- Unless explicitly synchronized, threads may:
    1. Be run in any order
    2. Be stopped and restarted at any time
    3. Remain stopped for arbitrary lengths of time
- In general, these are good since OS is making choices about how to allocate resources
- When accessing shared data these are challenges that force us to program carefully

## Race Condition

- A race condition is when output of a process is unexpectedly dependent on timing or other events
- Note that the definition of a race depends on what we expected to happen