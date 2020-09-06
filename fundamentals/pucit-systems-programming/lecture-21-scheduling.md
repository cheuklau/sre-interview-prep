# Lecture 21

## CPU Scheduler

- Scheduling manages queues to minimize queuing delay and to opotimize performance in a queueing environment
- Process scheduler in a multitasking operating system is a kernel coponent deciding which process too run, when and for hoow long
- Multi-tasking OOS comes in two flavors:
    1. Preemptice multitasking
        * Scheduler decides when a process is to ocease ruunning e.g., time slice expires
        * New proocess begins running
        * On many modern OS, time slice is dynamically calculated as a fracction of process behavior and configuratve system policy
    2. Cooperative multitasking
        * Process does nto stop running until it voluntarily deides too do so

## Preemptive vs Non-preemptive kernels

- At any instant, system can either be executing user mode or kernel mode
- This can happen:
    1. In process context (system call made by programmer)
    2. In interrupt context
- Three types of OS kernel:
    * Preemptive kernel: kernel that can be preempted in booth 1 and 2 abovoe
    * Reentrant kernel: kernel that can be preempted in A only
    * Non-preemptive kernel: kernel cannot be preempted

## Types of Processes

- Three main classes:
    1. Interactive processes
        * INteract constantly with users
        * Input received, average delay must fall between 50-150 ms or user will find system unresponsive
        * Typical interactive programs are command shells, text editors, graphical apps
    2. Batch processes
        * Do not need user interactioom and execute int he backgrouond
        * Often penalized by the scheduler
        * Programming langauge compilers, DB search engines, scientific computations
    3. Real-time processes
        * Short guaranteed response time with minimum variance
        * Multimedia apps, robot controllers, sensors data collectors
- Futher divided into:
    * I/O bound process
        * Spend moost time submitting and waiting on I/O requests e.g., waiting on user interactions via keyboaord and mouse
    * Processor bound process
        * Spend most time executing code e.g., executing loooop oor video encoder
    * Note: Above classifications not mutually exclusive
- Optimization scheduler criteria
    * Maximize:
        1. CPU utilization
        2. Throoughput
        3. Fairness
    * Minimize:
        1. Waiting time
        2. Response time
        3. Turnaround time
- Standard scheduling algorithms
    * FCFS
    * SJF
    * HRRN
    * Priority based
    * Round Robin
    * MLFQ
    * RSDL

## Traditional UNIX SVR3 Scheduler

- Contains 32 run queues from 0 to 31
- Queues implement round robin with quantum of 120 ms
- 128 priority values:
    * 0-49: kernel
    * 50-127: user level programs
- 4 priorities are mapped to each queue
    * Lower priority number = higher priority
    * 0-3 priorities mapped to run queue 0
    * 4-7 priorities mapped to run queue 1
    * etc
- Priority calculated by:
    * `usrpri_i(i)=Base_i+cpu(i)+nice_i`
        + `Base_i = 50`
        * `cpu(i)=decay rate*cpu(i-1)`
        * `nice_i` ranges from -20 to 19
    * Priority is re-calculated every second
    * Process moves from one queue to anoother
- Limitations
    * With large number of processes, overhead of recomputing process priorities every second is high
    * Since kernel is non-preemptive, high priority processes may have to wait for low priority processes executing in kernel mode

## Linux O(1) Scheduler

- Select next prcess to run in O(1) time
- Each processor keeps track of two arrays:
    1. Active array
    2. Expired array
- Each array has 140 queues implemented as a linked list with tasks represented by FIFO queue
    * 0-99 for kernel tasks
    * 100-139 for user tasks
- Once process has used up its quantum, it is moved to expired array
    * Its new quantum is calculated first, and new dynamic priority is calculated
    * When active array is empty, the two arrays are renamed
- Each array is also associated with two bitmaps of 140 bits each
    * Used to determine highest priority non-empty linked list in active array
- New processes inherit priorty from parent, time quantum it receives is half of parents
- Dynamic priority
    * `DP = max(100, min(SP-bonus+5, 139)`
    * Where bonus determined by average sleep time
- Time quantum calculation
    * Initial is paren't half
    * Minimum is 10ms (low interactivity, high nice)
    * Default is 100ms (average interactivity, zero nice)
    * Max is 200ms (high interactivity, nice low)
- Process may not necessarily run on same CPU it started
    * If process moves, cache from previous CPU must be invalidated
    * Cache of second must be populated with task data
    * CPU affinity is introduced
        * O(1) tries to ensure soft CPU affinity by assigning task back to original CPU
        * Can set hard CPU affinity via `schedtool`
- Limitations
    * Uses complex heuristics to determine if process is I/O bound or CPU bound
    * Lot of code to manage priority queues (at least 140 per processor)

## Completely Fair Share (CFS) Scheduler

- Used in latest kernel
- Rotating staircase
- Five scheduling classes from highest to lowest priority:
    1. Stop
        * Process in this class can preempt everything and is preempted by nothing
        * Example: Task migration, clock events
    2. Deadline
        * Used for periodic real-time tasks
        * `SCHED_DEADLINE`
    3. Real time
        * POSIX real-time tasks e.g., I/O queue threads with priorty values in range of 0 to 99
        * `SCHED_FIFO`
        * `SCHED_RR`
    4. CFS
        * Most user processes e.g., bash fall in this class
        * 100-139 priority values are mapped to -20 to +19
        * `SCHED_NORMAL`
        * `SCHED_BATCH`
        * `SCHED_ISO`
        * `SCHED_IDLEPRIO`
    5. Idle
        * No scheduling process
        * CPU will run when no oother tasks to run
- Scheduler iterates over each class in priority order
    * If a class has an eligble process, then it is run
    * Otherwise a turn of the lower priority process is run
    * If not idle process is run
- CFS scheduling class
    * Maintains time ordered red-black tree to manage list of runnable processes
    * Every proocess `task_struct` has a member `struct sched_entity`
    * `struct sched_entity` contains `struct rb_node` and `u64 vruntime`
        + `rb_node` represents every node of the tree
        + `vruntime` represents amount of time process has run and serves as index for red-black tree
    * Task with high priority i.e., lowest `vruntime` is at the left side of the tree
- No concept of time slice in CFS
    * When process is selected to run, its `vruntime` is implemented
    * Context switch occurs when `vruntime` of another task is smaller than currently running task
- `vruntime` of new proess
    * value is given so that it has a chance to shcedule quickly with good response time
- Priorities within a class
    * CFS does not use priorities directly
    * Uses as a decay factor of `vruntime`
    * Lower priority tasks have higher factors of decay
- How does CFS hand CPU bound and I/O bound proocesses
    * I/O bound process has low `vruntime`
    * CPU bound process has high `vruntime`

## Linux schedtool utility

- `ps -l -q $$` to see shell attributes
- `renice <new nice> <PID>`
- `nice <nice> <command>` to run command with nice value
- `sudo apt-get install schedtool`
- Used to query and change scheduling parameters
- `schedtool $$` to view shell PID, priority, CFS policy, Nice, Affinity
    * Note: `AFFINITY 0x7` is equivalent to `111` which means CPU can run on all three CPUs
- `schedtool -r` shows scheduling classes with min and max priority levels in each class
- `schedtool -B <PID>` to change scheduling policy of PID to `SCHED_BATCH`
- `schedtool -n <nice> <PID>` to change `nice` of PID
- `schedtool -a 0x2 <PID>` to make sure `PID` only runs on 2nd CPU
    * `0x2` is equivalent to `010`

## System calls related to scheduling

- `nice()`
- `getpriority()`
- `setpriority()`
- `sched_get_priority_min()`
- `sched_get_priority_max()`
- `sched_getscheduler()`
- `sched_getparam()`
- `sched_setparam()`
- `sched_yield()`: process to relinquish CPU
- `sched_rr_get_interval()`
- `sched_getcpu()`
- `sched_getaffinity()`
- `sched_setaffinity()`
- Example using `nice()`
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
extern int errno;
int main(){

   // System call to onice
   int nv = nice(+0);
   printf("Original nice value= %d\n", nv);
   nv = nice(+7);
   printf("Incrementing by nice(+7) = %d\n", nv);
errno = 0;
   nv = nice(-2); //only root can give a negative value
   if(nv==-1 && errno != 0){
	perror("nice(-2) failed");
	exit(1);
   }
   printf("Decrementing by nice(-2) = %d\n", nv);
   return 0;
}
```
- Example using `getpriority()` and `setpriority()`
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/time.h>
#include <sys/resource.h>
extern int errno;
int main(){
//get the nice value of calling process
   int nv = getpriority(PRIO_PROCESS, 0);
   printf("nice value of calling process = %d\n", nv);

//get the nice value of another process, e.g., parent process
   nv = getpriority(PRIO_PROCESS, getppid());
   printf("nice value of parent process = %d\n", nv);

//get the maximum possible nice value of process group of the calling process
   nv = getpriority(PRIO_PGRP, 0);
   printf("maximum nice value in calling Process Group = %d\n", nv);

//get the maximum possible nice value of user group of the calling process
   nv = getpriority(PRIO_USER, 0);
   printf("maximum nice value in the user group = %d\n", nv);

//change the nice value of calling process
errno = 0;
   nv = setpriority(PRIO_PROCESS, 0, -2);
   if(nv==-1 && errno != 0){
	perror("setpriority(PRIO_PROCESS, 0, -2) failed");
	exit(1);
   }
   nv = getpriority(PRIO_PROCESS, 0);
   printf("nice value after setpriority(PRIO_PROCESS, 0 , -2) = %d\n", nv);
   return 0;
}
```
- Example using `sched_get_priority_min()` and `sched_get_priority_max()`
```
#include <stdio.h>
#include <unistd.h>
#include <sched.h>

int main(){

   int min = sched_get_priority_min(SCHED_RR);
   printf("Minimum priority value for SCHED_RR = %d\n", min);
   int max = sched_get_priority_max(SCHED_RR);
   printf("Maximum priority value for SCHED_RR = %d\n", max);

   min = sched_get_priority_min(SCHED_FIFO);
   printf("Minimum priority value for SCHED_FIFO = %d\n", min);
   max = sched_get_priority_max(SCHED_FIFO);
   printf("Maximum priority value for SCHED_FIFO = %d\n", max);

   min = sched_get_priority_min(SCHED_OTHER);
   printf("Minimum priority value for SCHED_OTHER = %d\n", min);
   max = sched_get_priority_max(SCHED_OTHER);
   printf("Maximum priority value for SCHED_OTHER = %d\n", max);
   return 0;
}
```
- Example using `sched_rr_get_interval()`
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sched.h>

int main(){
//get the scheduling policy of the currently running process
   int s_policy = sched_getscheduler(getpid());
   printf("Scheduling policy of the current process = %d\n", s_policy);
//get the time slice
   struct timespec tp;
   int rv = sched_rr_get_interval(getpid(), &tp);
   if(rv == -1){
      printf("Error in getting the time slice\n");
      exit(1);
   }
   printf("Time Slice is %ld sec and %ld nanosecs \n", tp.tv_sec, tp.tv_nsec);
   return 0;
}
```