# Lecture 6

## Locks

- Locks are a synchronization primitive used to implement critical sections
- Threads release a lock when leaving a critical section
- Previously we covered spinlocks
    * Lock for the fact that it guards a critical section
    * Spin describing the process of acquiring it
- Spinlocks are rarely used on their own to solve synchronization problems
- Spinlocks are commonly used to build more useful synchronization primitives
- If we go back to the previous problem:
```
void giveGWATheMoolah(account_t account, int largeAmount) {
  int gwaHas = get_balance(account);
  gwaHas = gwaHas + largeAmount;
  put_balance(account, gwaHas);
  notifyGWAThatHeIsRich(gwaHas);
  return;
}
```
- We can apply a lock:
```
lock gwaWalletLock; // Need to initialize somewhere

void giveGWATheMoolah(account_t account, int largeAmount) {
+ lock_acquire(&gwaWalletLock);
  int gwaHas = get_balance(account);
  gwaHas = gwaHas + largeAmount;
  put_balance(account, gwaHas);
+ lock_release(&gwaWalletLock);
  notifyGWAThatHeIsRich(gwaHas);
  return;
}
```
- If we call `lock_acquire()` while another thread is in the critical section then the thread acquiring the lock must wait until the thread holding the lock calls `lock_release()`

## How to Wait

- Two ways to wait:
    1. Active waiting: repeat action until the lock is released
    2. Passive waiting: tell the kernel what we are waiting for, go to sleep, and rely on `lock_release()` to awaken us
- There are cases where spinning is the right thing to do. When?
    * Only on multi-core systems. Why?
        + On single core systems, nothing can change unless we allow another thread to run
    * If the critical section is short
        + Balance the length of the critical section against the overhead of a context switch

## How to Sleep

- The kernel provide functionality allowing kernel threads to sleep and wake on a `key`
- `thread_sleep(key)` tells the kernel, I (the process) is going to sleep, but please wake me up when `key` happens
- `thread_wake(key)` tells the kernel, please wake all the threads that were waiting for `key`
- Similar functionality can be implemented in user space


- Locks are designed to protect critical sections
- `lock_release()` can be considered a signal from the thread inside the critical section to other threads indicating that they can proceed
- What about other kinds of signals that I want to deliver e.g.,
    * The buffer has data in it
    * Child has exited

## Condition Variables

- We can do this using condition variables
    * A condition variable is a signaling mechanism allowing threads to:
        + `cv_wait` until a condition is true
        + `cv_notify` to notify other threads when the condition becomes true
- The condition is usually represented as some change to shared state e.g.,
    * The buffer has data in it `bufsize > 0`
    * `cv_wait`: notify me when buffer has data in it
    * `cv_signal`: I just put data in the buffer so notify the threads that are waiting for the buffer to have data
- Condition variable can convey more information than locks about some change to the state of the world
    * Example: buffer can be full, empty or neither
    * If buffer full, we can let threads withdraw but not add items
    * If buffer empty, we can let threads add but not withdraw
    * If buffer is neither full nor empty we can let threads add and withdraw items
    * We have three different buffer state and two different threads (producer and consumer)

## Locking Multiple Resources

- Locks protect access to shared resources
- Threads may need multiple shared resources to perform some operation
- Example:
    * Consider two threads `A` and `B` that both need simultaneous access to resources `1` and `2`
    1. Thread `A` runs, grabs lock for resource `1`
    2. Context switch
    3. Thread `B` runs, grabs lock for resource `2`
    4. Context switch
    5. Thread `A` runs, tries to acquire lock for resource `2`
    6. Thread sleeps
    7. Thread `B` runs, tries to acquire lock for resource `1`
- Both threads will never wake up as they have a circular dependency
    * This is referred to as a deadlock
- Self deadlock happends when a single thread is in a deadlock
    * Thread `A` acquires resource `1`
    * Thread `A` then tries to reacquire resource `1`
    * Why would this happen?
        + `foo()` needs resource `1`, `bar()` needs resource `1`
        + While locking resource `1`, `foo()` calls `bar()`
    * Solve this problem with recursive locks where we allow a thread to reacquire a lock that it already hoolds as long as calls to acquire are matched by calls to release
    * This is fairly common

## Conditions for Deadlock

- A deadlock cannot occur unless all of the following conditions are met:
    1. Protected access to shared resources which implies waiting
    2. No resource preemption meaning that thesystem cannot forcibly take a resource from a thread holding it
    3. Multiple independent requests, meaning a thread can hold some resources while requesting others
    4. Circular dependency graph meaning that Thread `A` is waiting for Thread `B` which is waiting for Thread `C` which is waiting for Thread `D` which is waiting for Thread `A`

## Deadlock vs Starvation

- Starvation is an equally problematic condition in which one or more threads do not make progress
    * Starvation differs from deadlock in that some threads make progress and it is, in fact, those threads that are preventing the starving threads from proceeding

## Producer-Consumer

- Producer and consumer share a fixed-size buffer
- Producer can add items to the buffer if it is not full
- Consumer can withdraw items from the buffer if it is not empty
- Ensure:
    1. Producer wait if buffer is full
    2. Consumer must wait if buffer is empty
    3. Producers should not be sleeping if there is room in the buffer
    4. Consumers should not be sleeping there are items in the buffer