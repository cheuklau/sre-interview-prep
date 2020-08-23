# Lecture 12

## Scheduling

- Scheduling is the process of choosing the next thread (or threads) to run on the CPU (or CPUs)
- Why schedule threads?
    * CPU multiplexing: we have more threads than cores to run them on
    * Kernel prvilege: we are in charge of allocating the CPU and must try to make good decisions
- When does scheduling occur?
    * When a thread voluntarily gives up the CPU by calling `yield()`
    * When a thread makes a blocking system call and must sleep until the call completes
    * When a thread exits
    * When the kernel decides that a thread has run for long enough
        + This is what makes a scheduling policy preemptive as opposed to cooperative
        + Kernel can preempt (i.e., stop) a thread that has not requested to be stopped
- What is the rationale behind having a way for threads to voluntarily give up the CPU?
    * `yield()` can be useful way of allowing well-behaved thread to tell CPU it has no more useful work to do
    * `yield()` is inherently cooperative i.e., "let me get out of the way so that another, more useful, thread can run"
- How do I schedule threads?
    * Mechansim: how do we switch between threads?
    * Policy: how do we choose the next thread to run?
- How do we switch between threads?
    * Perform a context switch and move threads between the ready, running and waiting queues

## Policy vs. Mechanism

- Scheduling is an example of useful separateion between policy and mechanism:
    * Policies
        + Deciding what thread to run
        + Giving preference to interactive tasks
        + Choosing a thread to run at random
    * Mechanisms:
        + Context switch
        + Maintaining the running, read and waiting queues
        + Using timer interrupts to stop running threads

## Scheduling Matters

- How the CPU is scheduled impacts every other part of the system
    * Using other system resources requires the CPU
    * Intelligent scheduling makes a modestly-powered system seem fast and responsive
    * Bad scheduling makes a powerful system seem sluggish and laggy
- Responsiveness: when you give computer an instruction and it responds in a timely manner
    * May not finish, but at least you know it started
    * Most of what we do with computers consist of responsive tasks
    * Examples: web browsing, editing, chatting
- Continuity: when you ask computer to perform a continuous task it does so smoothly
    * Implies active waiting: not interacting with computer but you are expecting it to continue to perform a task you have initiated
    * Examples: blinking cursor, playing music or a movie
- Completion: when we ask the computer to perform a task (or it performs one on our behalf) that we expect to take a long time, we want it to complete eventually
    * Implies passive waiting: asking computer to continue to deliver interactive performance while working on your long-running task
    * Unlike responsive and continuous task, background tasks may not be user initiated
    * Examples: performing a system backup, indexing files on computer
- Conflicting goals
    * Scheduling is a balance between meeting deadlines and optimizing resource allocation
        + Optimal resource allocation: allocate tasks so that all resources constantly in use
        + Meeting deadlines: drop everything and do a certain task
    * Responsiveness and continuity require meeting deadlines
        + Responsiveness have unpredictable deadlines e.g., when user moves the mouse, I need to be ready to redraw the cursor
        + Continuity have predictable deadlines e.g., every 5ms I need to write more data to the sound card buffer
    * Throughput requires careful resource allocation
        + Throughput require optimal resource allocation e.g., I should really give the backup process more resources so that it can finish overnight
- Deadlines win
    * Humans are sensitive to responsiveness and continuity
    * We don't notice resource allocation as much
    * Poor responsiveness or continuity wastes our time

## Scheduling Goals

- How well does it meet deadlines (unpredictable or predictable)
- How completely does it allocate system resources
    * No point having idle CPU, memory or disk bandwidth when something useful could be happening
- On human-facing systems, typically deadlines win
- For human-facing systems, if system doesn't meet deadlines it is typically just annoying e.g., buffering
- For other classes of systems, failure to meet deadlines could be fatal