# Lecture 11

## Threads

- What is a thread?
    * Registers
    * Stack
- How are each of the following shared between threads or processes?
    * Registers (private to thread)
    * Stack (private to thread)
    * Memory - shared between multiple threads (part of process)
    * File descriptor table - shared between multiple threads (part of process)

## Why Use Threads?

- Threads can be a good way of thinking about apps that do multiple things "simultaneously"
- Threads may naturally encapsulate some data about a certain thing that the app is doing
- Threads may help apps hide or parallelize delays caused by slow devices

## Threads vs Events

- While threads are a reasonable way of thinking about concurrent programming, they are not the only way to make use of system resources
- Another approach is event-driven programming
- Anyone who has done Javascript development or used frameworks e.g., `node.js` has grown familiar with this programming model
- Simplification of events vs threads:
    * Threads can block so we make use of the CPU by switching between threads
    * Even handlers cannot block so we can make use of the CPU by simply running events until completion

## Naturally Multithreaded Applications

- Web server
    * Use a separate thread to handle each incoming requeset
- Web browser
    * Separate threads for each open tab
    * When loading a page, separate threads to request and receive each unique part of the page
- Scientific applications
    * Divide-and-conquer parallelizable datasets

## Why Not Processes?

- IPC is more difficult because kernel tries to protect processes from each other
    * Inside a single process, anything goes
- State associated with processes that doesn't scale very well

## Implementing Threads

- Threads can be implemented in userspace by unprivileged libraries
    * This is the `M:1` threading model
        + `M` user threads that look like `1` thread to the OS kernel
- Threads can be implemented by the kernel directly
    * This is the `1:1` threading model

## Implenting Threads in Userspace

- How is this possible?
    * Doesn't involve multiplexing between processes so no kernel privilege required
- How do I:
    * Save and restore context?
        + Just saving and restoring registers
        + C library has an implementation called `setjmp()` and `longjmp()`
    * Preempt other threads?
        + Use periodic signals delivered by the OS to activate a userspace thread scheduler

## Comparing Thrading Implementations

- `M:1` userspace threading
    * Pros:
        + Threading operations are much faster because they do not have to cross the user/kernel boundary
        + Thread state can be smaller
    * Cons:
        + Can't use multiple cores
        + OS may not schedule the app correctly because it doesn't know about the fact that it contains more than one thread
- `1:1` kernel threading
    * Pros:
        + Scheduling might improve because kernel can schedule all threads in the process
    * Cons:
        + Context switch overhead for all threading operations

## Thread States

- Several different states:
    1. Running: executing instructions on CPU core
    2. Ready: not executing instructions but capable of being restarted
    3. Waiting, blocked, sleeping: not executing instructions and not able to be restarted until some event occurs
- Transitions:
    1. Running to ready: thread was descheduled
    2. Running to waiting: thread performed a blocking system call
    3. Waiting to ready: event thread was waiting for happened
    4. Ready to running: thread was scheduled
    5. Running to terminated