# Lecture 32

## OS Performance

1. Measure your system
    * How and doing what?
        + High level software counters may not have fine enough resolution to measure extremely fast events
        + Low level hardware counters may have extremely device-specific interfaces making cross-platform measurements more difficult
        + Measurements should be repeatable right?
            - Wrong, you are measuring the present but rest of system is trying to use the past to predict the future
            - In generate real systems are almost never in the exact same state as they were last time you measured whatever you are trying to measure
        + Measurements tends to affect the thing that you are trying to measure
            - This has three results:
                1. Measurement may destroy the problem you are trying to measure
                2. Must separate results from the noise produced by measurement
                3. Measurement overhead may limit your access to real systems
        + This is even more fraught given how central the OS is to the operation of computer itself
            - Difficult to find the appropriate places to insert debugging hooks
            - OS can generate a lot of debugging output e.g., imagine tracing every page fault
    * Benchmarking real systems seem real hard. What else can we do?
        + Build a model: abstract away all of the low-level details and reason analytically
        + Build a simulator: write some additional code to perform a simplified simulation of more complex parts of the system - particularly hardware
    * Models:
        + Pros:
            - Can make a strong mathematical guarantees about system performance
        + Cons:
            - Usually after making a bunch of unrealistic assumptions
    * Simulations:
        + Pros:
            - Best case, experimental speedup outweights lack of hardware details
        + Cons:
            - Worst case, bugs in the simulation leads you in all sorts of wrong directions
    * What metric do I use to compare:
        + Two disk drives
        + Two scheduling algorithms
        + Two page replacement algorithms
        + Two file systems
    * Microbenchmarks: isolate one aspect of system performance
        + Example: measuring virtual memory system
            - Time to handle single page fault
            - Time to look up page in the page table
            - Time to choose a page to evict
        + Problem: may not be studying the right thing
    * Macrobenchmarks: measure one operation involving many parts of the system working together
        + Example: measuring virtual memory system
            - Aggregate time to handle page faults on a heavily-loaded system
            - Page fault rate
        + Problem: introduces many, many variables that can complicate analysis
    * Application benchmarks: focus on the performance of the system as observed by one application
        + Example: measuring virtual memory system
            - `triplesort`
            - `parallelvm`
        + Problem: improvements for the app may harm others
    * Benchmark bias
        + People choosing and running benchmarks may be trying to justify some change by making their system look faster
        + Alternatively people chose a benchmark and did work to improve its performance while ignoring other effects on the system
    * Fundamental tension: most useful system is general purpose but the fast system is a single purpose system
2. Analyze the results
    * Use statistics
3. Improve the slow parts
    * How and which slow parts?
4. Repeat

