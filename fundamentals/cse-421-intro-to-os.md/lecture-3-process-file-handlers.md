# Lecture 3

## Processes
- `ps aux | grep bash` to view bash processes running
- `pgrep bash` to view PID of bash processes
- `ps -Lf <PID>` to view threads
    * `UID` = user running the process
    * `PID`
    * `PPID`
    * `LWP` = lightweight process i.e., thread ID
    * `PRI` = scheduling priority
    * `SZ` = size of core image (kB)
    * `WCHAN` = if process is running, description of what it is waiting on
    * `RSS` = total amount of resident memory in use by process (kB)
    * `TIME` = measure of amount of time process spent running
- `pmap <pid>` to show mapping between process address space and content
    * `0005637ceb00000 1368K r-x-- systemd`
    * `<memory address space> <size> <permissions> <content e.g., executable, libraries>`
    * Note: `anon` = memory used by process for its heap
    * Note: `stack` = memory used by process for its stack
- `lsof -p <pid>` to list open files of a process
    * Note: `/dev/pts/0` indicates open terminal
- Information obtained by `ps`, `pmap`, `lsof` is from `/proc` filesystem
    * No disk block storing the `/proc` filesystem
    * Linux creates these pseudofiles

## File Handles

- File descriptor that processes receive from `open()` and pass to other file system calls is just an integer, an index into the process file table
- That integer refers to a file handle object maintained by the kernel
- That file handle object contains a reference to a separate file object also maintained by the kernel
- The file object is mapped by the file system to blocks on disk
- Three levels of indirection:
    1. File descriptor --> file handle
    2. File handle --> file object
    3. File object --> blocks on disk
- Why this extra indirection with the file handle?
    * Allows certain pieces of state to be shared separately
    * File descriptors are private to each process
    * File handles are private to each process but shared after process creation
        + File handles store the current file offset or position in the file that the next read will come from or write will go to
        + File handles can be deliberately shared between two processes
    * File objects hold other file state and can be shared transparently between many processes
    * This follows an OS design principle of separating policy from mechanism
    * This also facilitates control or sharing by adding a level of indirection

## fork: Create a New Process

- `fork()` is the system call to create a new proocess
    * `fork()` creates a new process that is a copy of the calling process
    * After `fork()` completes, we refer to the caller as the parent and the newly created process as the child
- Generally `fork()` tries to make an exact copy of the calling process
- Threads are a notable exceptioon
- Single-threaded `fork()` has reliable semantics because the only thread process had is the one that called `fork()`
    * So nothing else is happening while we complete the system call
- Multi-threaded `fork()` creates a host of problems that many systems choose to ignore
    * Linux will only copy state for the thread that called `fork()`
    * Two major problems with multi-threaded `fork()`
        1. Another thread could be blocked in the middle of doing something (uniprocessor systems)
        2. Another thread could be actually doing something (multiprocessor systems)
    * This ends up being a mess so we just copy the calling thread
- `fork()` copies
    * One thread -- the caller
    * The address space
    * The process file table
- `fork()` returns two times
    * The child thread returns executing at the exact same poiont that its parent called `fork()`
    * `fork()` returns twice: the PID to the parent and 0 to the child
- All contents oof memory in the parent and child are identical
- Both child and parent have the same files open at the same position but since they are sharing file handles changes to the file made by the parent or child will be reflected in the other
