# Lecture 27

## Computers Circa 1991

- Disk bandwidth is improving rapidly, meaning OS can stream reads/writes to the disk faster
- Computers have more memory (up to 128MB)
- Disk seek times still slow

## Using what we Got

- So if we can solve this seek issue, we can utilize growing disk bandwidth to improve filesystem performance
    * We have a bunch of spare memory, maybe that can be useful

## Use a Cache

- How do we make a big slow thing look faster
    * Use a cache
    * In this case of the file system, the smaller faster thing is memory
    * We call the memory used to cache file system data the buffer cache
- With a large cache, we should be able to avoid doing almost any disk reads
- But we still have to do disk writes, but cache will still help collect small writes in memory until we can do one larger write

## Log Structured File Systems

- All writes go to an append-only log
- Example: change an existing byte in a file:
    1. Seek to read the inode map
    2. Seek to read the inode
    3. Seek to write the data block
    4. Seek to write the inode
- For a cached-read write:
    1. Read the inode map from cache
    2. Read the inode from cache
    3. Seek to write the data block
    4. Seek to write the inode
- For an LFS write:
    * Reads are handled by the cache and writes can stream to the disk at full bandwidth due to short seeks to append to the log
- When do we write to the log?
    * When the user calls `sync`, `fsync` or when blocks are evited from the buffer cache

## Locating LFS Inodes

- How did FFS translate an inode number to disk block
    * It stored the inode map in a fixed location on disk
- Why is this a problem for LFS
    * Inodes are just appended to the log and so they can move
- And so what do you think LFS does about this?
    * It logs the inode map

## LFS Metadata

- What about file system metadata: inode and data block allocation bitmaps, etc
    * We can log that stuff too

## As the Log Turns

- What happens when the log reaches the end of the disk
    * Probably a lot of unused space earlier in the log due to overwritten inodes, data blocks, etc
- How do we reclaim this space?
    * Clean the log by identifying empty space and compacting used blocks
- Conceptually you can think of this happening across the entire disk all at once, but for performance reasons LFS divides the disk into segments which are cleanly separated

## The Devil is in the Cleaning

- LFS seems like a great idea until you think about cleaning

## Cleaning Questions

- When should we run the cleaner?
    * Probably when the system is idle which may be a problem on systems that don't idle much
- What size segments should we clean?
    * Large segments amortize the cost to read and write all of the data necessary to clean the segment
    * But small segments increase the probability that all blocks in a segment will be dead making cleaning trivial
- What other effect does log cleaning have?
    * Cleaner overhead is very workload-dependent making it difficult to reason about the performance of log-structure file system

## Reading Questions

- Let's say that the cache does not soak up as many reads as we were hoping
- What problem can LFS create?
    * Block allocation is extremely discontiguous, meaning that reads may seek all over the disk
