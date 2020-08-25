# Lecture 20

## Page Eviction

- In order to swap out a page we need to choose which page to move to disk
- In order to swap in a page we might need to chooose which page to swap out
- Swapping cost-benefit calculation:
    * Cost: mainly time and disk bandwidth required to move a page to and from disk
    * Benefit: Use of 4K (or a page) of memory as long as the page on disk remains unused
- There are tricks that the OS might play to minimize the cost, but mainly we focus oon algorithms that maximize the benefit
- Another complementary description of our goal is minimizing the page fault rate

## Maximizing Benefit

- Benefit: use of 4K memory as long as the page on disk remains unused
- How do we maximize the benefit:
    * Pick the page to evict that will remain unused the longest

## Best Case Scenario

- What is the absolute best page to evict, the one that page replacement algorithms dream about?
    * A page that will never be used again

## Thrashing

- Virtual memory subsystem is in constant state of paging, rapidly exchanging data in memory for data on disk
- Causes performance of the computer to degrade or collapse

## Break Out the Ball

- What would we like to know about a page when choosing one to evict?
    * How long will it be before this page is used again?
- The optimal scheduler evicts the page that will remain unused the longest
- This clearly maximizes our swapping cost-benefit calculation

## Past Didn't Go Anywhere

- Intelligent page replacement requires three things:
    1. Determining what information to track
    2. Figuring out how to collect that information
    3. How to store it

## There are Tradeoffs

- Collecting statistics may be expensive, slowing down the prcess of translating virtual addresses
- Storing statistics may be expensive, occupying kernel memory that cuold be used for other things

## Simplest

- What is simplest possible page replacement algorithm
    * Random
- Pros
    * Easy
    * Good baseline for algorithms that may try to be smarter
- Cons
    * Too simple

## Use the Past

- What is an algorithm that uses a page's past to predict its future
    * Least recently used
    * Choose page that has not been used for the longest period of time
    * Hopefully this is a page that will not be used for a while
- Pros
    * Good as we can do without predicting the future
- Cons
    * How do we tell how long it has been since a page has been accessed

## LRU: Collecting Statistics

- At what point does OS know that a process has accessed a virtual page?
    * When we load the entry into the TLB
- Does this reflect every virtual page access?
    * No, only the first
    * A page that is accessed once and one that is accessed 1000 times are indistinguishable
- Why not record every page access?
    * Too slow

## LRU: Storing Statistics

- How much access time information can we store?
    * 32 bits = 2^32 ticks but doubles the page table entry size
    * 8 bits = 256 ticks
- How do we find the least recently used page?
    * Need soome kind of efficient data structure holding all physical pages on the system that is searched on every page eviction

## Clock LRU

- Simple and efficient LRU-like algorithm
- One bit of accessed information, set when loading a virtual address into the TLB
- To locate a page to evict:
    1. Cycle through all pages in memory in a fixed order
    2. If a page accessed bit is clear, evict that page
    3. If a page accessed bit is set, clear the bit
- If clock hand turning slowly
    * Little memory pressure
    * Making good decisions on what to evict
- If clock hand turning rapidly
    * Lots of memory pressure
    * Making bad decisions on what to evict