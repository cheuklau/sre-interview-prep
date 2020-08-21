# Lecture 5

## Review

- Reduce synchronization as much as possible so multi-thread process is correct
- Increase concurrency as much as possible so multi-thread process is fast

## Concurrency vs. Atomicity

- Concurrency: the illusion that multiple things are happening at once
    * Requires stopping or starting any thread at any time
- Atomicity: the illusion that a set of separate actions occurred all at once
    * Requires not stopping certain threads at certain times or not starting certain threads at certain times
    * Providing some limited control to threads over their scheduling

## Critical Sections

- Critical section contains a series of instructions that only one thread can be executing at any given time
- Questions to ask:
    1. What is the local state private to each state?
    2. What is the shared state that is being accessed by multiple threads?
    3. What lines are in the critical section?
- Example
```
void giveGWATheMoolah(account_t account, int largeAmount) {
  int gwaHas = get_balance(account);
  gwaHas = gwaHas + largeAmount;
  put_balance(account, gwaHas);
  notifyGWAThatHeIsRich(gwaHas);
  return;
}
```
- In above example:
    1. `gwaHas` is local state private to each thread
    2. `account` is the shared state accessed by multiple threads
    3. Lines 2-4 need to be in a critical section
- Critical section requirements:
    1. Mutual exclusion: only one thread should be executing in the critical section at a time
    2. Progress: all threads should eventually be able to proceed through critical section
    3. Performance: keep critical sections as small as possible without sacrificing correctness

## Implementing Critical Sections

- Two possible appraches:
    1. Don't stop
    2. Don't enter
- On uniprocessors, a single thread can prevent other threads from executing in a critical section by not being descheduled
    * In the kernel we can do this by masking interrupts (no timer, no scheduler, no stopping)
    * In the multi-core era, this is only of historical interest
- More generally we need a way to force other threads (potentially running on other cores) not to enter the critical section while one thread is inside
    * How do we do this?

## Atomic Instructions

- Software synchronization primitives utilize special hardware instructions guaranteed to be atomic across all cores
    * Test-and-set: write a memory location and return its old value
    ```
    int testAndSet(int * target, int value) {
        oldvalue = *target;
        *target = value;
        return oldvalue;
    }
    ```
    * Compare-and-swap: compare the contents of a memory location to a given value. If the same then set variable to a new given value
    ```
    bool compareAndSwap(int * target, int compare, int newvalue) {
        if (*target == compare) {
            *target = newvalue;
            return 1;
        } else {
            return 0;
        }
    }
    ```
    * Load-link and store-conditional: load-link returns the value of a memory address while the following store-conditional succeeds only if the value has not changed since load-link
    ```
    y = 1;
    __asm volatile(
        ".set push;"     /* save assembler mode */
        ".set mips32;"   /* allow MIPS32 instructions */
        ".set volatile;" /* avoid unwanted optimization */
        "ll %0, 0(%2);"  /*   x = *sd */
        "sc %1, 0(%2);"  /*   *sd = y; y = success? */
        ".set pop"       /* restore assembler mode */
        : "=r" (x), "+r" (y) : "r" (sd));
    if (y == 0) {
    return 1;
    }
    ```
- Many processors provide either test-and-set or compare-and-swap
    * Modify example from earlier:
    ```
    +int payGWA = 0; // Shared variable for our test and set.

    void giveGWATheMoolah(account_t account, int largeAmount) {
        if (testAndSet(&payGWA, 1) == 1) {
        // Keep looping until testAndSet is unlocked
        }
        int gwaHas = get_balance(account);
        gwaHas = gwaHas + largeAmount;
        put_balance(account, gwaHas);
        testAndSet(&payGWA, 0); # Clear the test and set.
        notifyGWAThatHeIsRich(gwaHas);
        return;
    }
    ```
    * Busy waiting: threads wait for the critical section by "pounding on the door" executing test-and-set repeatedly
    * This is bad on a multi-core system (worse on a single core system) since busy waiting prevents the thread in the critical section from making progress

## Locks

- Locks are a synchronization primitive used to implement critical sections
    * Threads acquire a lock when entering a critical section
    * Threads release a lock when leaving a critical section

## Spinlocks

- What we implemented in the example is known as a spinlock
    * Lock for the fact that it guards a critical section
    * Spin describing the process of acquiring it
- Spinlocks are rarely used on their own to solve synchronization problems
- Spinlocks are commonly used to build more useful synchronization primitives