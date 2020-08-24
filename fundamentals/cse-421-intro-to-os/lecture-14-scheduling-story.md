# Lecture 14

## Oracular Spectacular

- Normally we cannot predict the future
    * Control flow is unpredictable
    * Users are unpredictable
- Instead we use the past to predict the future
    * What did the thread do recently? It will probably keep doing that

## Multi-Level Feedback Queues

- Choose a scheduling quantum
- Establish some number of queues each representing a level
- Threads from the highest-level queues are chosen first
- Then:
    1. Choose and run a thread from the highest-level non-empty queue
    2. If the thread blocks or yields, promote it to a higher level queue
    3. If the thread must be preempted at the end of a quantum, demote it to a lower level queue
- What happens to:
    * CPU-bound threads? They descend to the depths
    * I/O-bound threads? They rise to the heights
- Can anyone spot any problems with this approach?
    * Starvation i.e., threads trapped in the lower queues may never have a chance to run
- One solution is to periodically rebalance the levels by tossing everyone back to the top level

## Establishing Priorities

- Priorities are a scheduling abstraction that allows user or system to assign relative importance between tasks
- For example:
    * Backup task: low priority
    * Video encoding: low priority
    * Video playback: high priority
    * Interactive apps: medium priority
- Priorities are always relative

## Priority Starvation

- Strict priorities can lead to starvation when low-priority threads are constantly blocked by high-priority threads with work to do
- One solution is lottery scheduling:
    1. Give each thread a number of tickets proportional to their priority
    2. Choose a ticket at random - the thread holding the ticket gets to run
- Priorities may also be used to determine how long threads are allowed to run i.e., dynamically adjusting their time quantum

## Linux Scheduling Pre-2.6

- Scheduler scaled poorly requiring O(n) time to schedule tasks where n is the number of runnable threads

## Linux 2.6 Scheduler

- Linux kernel scheduler maintainer implemented a new O(1) scheduler to address scalability issues with eaerlier approach
- O(1) scheduler combines a static and dynamic priority
    * Static priority: set by user or system using `nice`
    * Dynamic priority: potential boost to static priority intended to reward interactive threads

## Rotating Staircase Deasdline Scheduler (RSDL)

- One parameter: round-robin interval
- One input: thread priority
- Priority defines levels at which task can run
    * High priority tasks: more levels, more chances to run
    * Low priority tasks: fewer levels, fewer chances to run
- Tasks can run for at most a fixed amount of time per level
- Each level can also run for at most a fixed amount of time

## RSDL

- To begin a scheduling epoch:
    1. Put all threads in a queue determined by priority
    2. If a thread blocks or yields, remains at level
    3. If thread runs out of quaota, moves to next level down
    4. If level runs out of its quota, all threads move to the level down
    5. Continue until all quotas exhausted or no threads are runnable, then restart another epoch

## RSDL Pros

- Easily calculate how long it will be before a thread at a certain priority level runs
- Simple, fixed accouting; scheduling is O(1)
- More recent versions use interleaving to further reduce delay between tasks scheduling with different priorities