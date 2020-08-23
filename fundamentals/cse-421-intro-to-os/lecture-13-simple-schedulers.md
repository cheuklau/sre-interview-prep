# Lecture 13

## Scheduling Information

- Schedulers use three kinds of additional information in order to choose which thread to run next:
    1. What will happen next?
        * Orachular schedulers cannot be implemented but can be a good point of comparison
    2. What just happened?
        * Typical schedulers (and many other OS algorithms) use the past to predict the future
    3. What does the user want?
        * Schedulers usually have ways to incorporate user input

## Random Scheduling

- Choose a scheduling quantum
    * Maximum amount of time any thread will be able to run at one time
- Then:
    1. Choose a thread at random from the ready pile
    2. Run the thread until it blocks or the scheduling quantum expires
- What happens when a thread leaves the waiting state?
    * Just return it to the ready pile

## Round-Robin Scheduling

- Choose a scheduling quantum
- Establish an ordered ready queue. For example, when a thread is created add it to the tail of the ready queue.
- Then:
    1. Choose the thread at the head of the ready queue
    2. Run the thread until it blocks or the scheduling quantum expires
    3. If its scheduling quantum expires, place it at the tail of the ready queue
- What happens when a thread leaves the waiting state?
    * Could put it at the head of the ready queue or at the tail

## The Know Nothings

- The random and round-robin scheduling algorithms
    * Require no information about a thread's past, present or future
    * Accept no user input
- These are rarely used algorithms except as straw men to compare other approaches to
- Both penalize (or at least do not reward) threads that give up the CPU before quantums expire
- As one exception, round robin scheduling is sometimes used once other scheduling decisions have been made and a set of threads are considered equivalent
    * As an example, you might rotate round-robin through a set of threads with the same priority

## The Know-It-Alls

- What might we like to show about threads we are about to execute:
    1. How long is it going to use the CPU?
    2. Will it block or yield?
    3. How long will it wait?

## Shortest Job First

- Why would we use this algorithm?
    * Minimizes wait time
- More generatlly, why would we prefer threads that give up the CPU before their time quantum ends?
    * They are probably waiting for something else which can be done in parallel with CPU use