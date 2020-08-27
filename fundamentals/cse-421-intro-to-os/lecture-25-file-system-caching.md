# Lecture 25

## Making File Systems Fast

- How do we make a big slow thing look faster?
    * Use a cache
- In this case of the file system, the smaller, faster thing is memory
- We call the memory used to cache file system data the buffer cache

## Putting Spare Memory to Work

- OS use memory
    * As memory
    * To cache file data in order to improve performance
- These two uses of memory compete with each other
    * Big buffer cache, small main memory: file access is fast, but potential thrashing in the memory subsystem
    * Small buffer cache, large main memory: little swapping occurs but file access is extremely slow
- On Linux the `swappiness` kernel parameter controls how aggressively the OS prunes unused process memory pages and hence the balance between memory and buffer cache

## Where to Put the Buffer Cache?

## Above the File System

- What do we cache?
    * Entire files and directories
- What is the buffer cache interface
    * `open`, `close`, `read`, `write` (same as the file system call interface)

## Above the File System: Operations

- `open`
    * Pass down to underlying file system
- `read`
    * If file is not in the buffer cache, pass load contents into the buffer cache and then modify them
    * If file is in the cache, modify the cached contents
- `write`
    * If file is not in buffer cache, pass load contents into the buffer cache and then modify them
    * If file is in the cache, modify the cached contents
- `close`
    * Remove from the cache (if necessary) and flush contents through the file system

## Above the File System: Pros and Cons

- Pros:
    * Buffer cache sees file operations, may lead to better prediction or performance
- Cons:
    * Hides many file operations from the file system, preventing it from providing consistency guarantees
    * Can't cache file system metadata: inodes, superblocks, etc

## Below the File System

- What do we cache?
    * Disk blocks
- What is the buffer cache interface?
    * `readblock`, `writeblock` (same as the disk interface)

## Below the File System: Pros and Cons

- Pros:
    * Can cache all blocks including file system data structures, inodes, superblocks, etc
    * Allows file system to see all file operations even if they eventually hit the cache
- Cons
    * Cannot observe file semantics or relationships
- This is what modern OS do

## Review: Data Blocks: Multilevel Index

- Most files are small, but some can get very large
- Have inode store:
    * Some pointers to blocks which refer to direct blocks
    * Some pointers to blocks containing pointers to blocks which we refer to as indirect blocks
    * Some pointers to blocks containing pointers to blocks containing pointers to blocks which we refer to doubly indirect blocks
    * Etc.
- Pros:
    * Index scales with the size of the file
    * Offset lookups are still fairly fast
    * Small files stay small but big files can get extremely large

## Buffer Cache Location

- Where is buffer cache typically located?
    * Below the file system
- What does the buffer cache store?
    * Complete disk blocks including file system metadata

## Caching and Consistency

- How can the cache cause consistency problems?
    * Objects in the cache are lost on failures
- Remember: almost every file system operation involves modifying multiple disk blocks
- Example of creating a new file in an existing directory
    1. Allocate an inode, mark the used inode bitmap
    2. Allocate data blocks, mark the used data block bitmap
    3. Associate data blocks with the file by modifying the inode
    4. Add inode to the given directory by modifying the directory file
    5. Write data blocks

## How Caching Exacerbates Consistency

- Observation: file system operations that modify multiple blocks may leave the file system in an inconsistent state if partially complete
- How does caching exacerbate this situation?
    * May increase time span between when the first write of the operation hits the disk and the last is completed

## What Can Go Wrong?

- What kinds of inconsistency can take place if the system is interrupted between the multiple operations necessary to complete a write?
    1. Allocate an inode, mark the used inode bitmap (incode incorrectly marked in use)
    2. Allocate data blocks, mark the used data block bitmap (data blocks incorrectly marked in use)
    3. Associate data blocks with the file by modifying the inode (dangling file not present in any directory)
    4. Add inode to the given directory by modifying the directory file
    5. Write data blocks (data loss)

## Maintaining File System Consistency

- What is the safest approach?
    * Do not buffer writes
    * We call this a write through cache because writes do not hit the cache
- What is the most dangerous approach?
    * Buffer all operations until blocks are evicted
    * We call this a write back cache
- What approach is better for
    * Performace
    * Safety
- What about a middle ground?
    * Write important file system data metadata structures (superblock, inode, bitmaps, etc) immedately but delay data writes
- File systems also give use processes some control through `sync` (sync the entire file system) and `fsync` (sync one file)