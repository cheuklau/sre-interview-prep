# Lecture 26

## Another Approach to Consistency

- What's not atomic: writing multiple disk boots
- What is atomic: writing one disk block

## Journaling

- Track pending changes to the file system in a special area on disk called the journal
- Following a failure, replay the journal to bring the file system back to a consistent state
- Creation example:
    * Dear Journal, here is what I am going to do:
        1. Allocate inode 567 for a new file
        2. Associate data blocks 5, 87, 98 with inode 567
        3. Add inode 567 to the directory with inode 33
        4. Done

## Journaling: Checkpoints

- What happens when we flush cached data to disk?
    * Update the journal
    * This is called a checkpoint
    * Dear Journal, here is what I'm going to do today:
        1. Allocate inode 567 for a new file
        2. Associate data blocks 5, 87, 98 with inode 567
        3. Add inode 567 to the directory with inode 33
        4. Done
    * Dear Journal, I already did everything mentioned above. Checkpoint!

## Journaling: Recovery

- What happens on recovery?
    * Start at the last checkpoint and move forward, updating on-disk structures as needed
    * Dear Journal, I already did everything mentioned above. Checkpoint!
    * Dear Journal, here is what I'm going to do today:
        1. Allocate inode 567 for a new file. Did this already!
        2. Associate data blocks 5, 87, 98 with inode 567. Didn't do this...okay done!
        3. Add inode 567 to the directory with inode 33. Didn't do this either...okay done!
        4. Done. All caught up!
- What about incomplete journal entries?
    * These are ignored as they may leave the file system in an incomplete state
- What would happen if we processed the following incomplete journal entry:
    1. Allocate inode 567 for a new file
    2. Associate data blocks 5, 87, 93 with inode 567

## Journaling: Implications

- Observation: metadata updates (allocate inode, free data block, add to directory, etc) can be represented compactly and probably written to the jounral atomically
- What about data blocks themselves changed by `write()`?
    * We could include them in the journal meaning that each data block would potentially be written twice
    * we could exclude them from the journal meaning that file system structures are maintained but not file data

## The Berkeley Fast File System

- First included in the Berkeley Software Distribution (BSD) UNIX
- FFS is the basis of the Unix File System (UFS) which is still in use today

## Exploiting Geometry

- FFS made many contributions to file system design
- Some were lasting others less so
    * Less lasting features had to do with tailoring file system performance to disk geometry
- What are some geometry-related questions that file systems might try to address
    * Where to put inodes
    * Where to put data blocks particularly where with respect to inodes that they are linked
    * Where to put related files
    * What files are likely to be related

## Introducing Standard File System Features

- FFS also responded to many problems with earlier file system implementations and introduced many common features we have already learned about
- Early file systems had a small block size of 512 B
    * FFS introduced 4K blocks
- Early file systems had no way to allocate contiguous blocks on disks
    * FFS introduced an ordered free block list allowing contiguous or near-contiguous block allocation
Early file systems lacked many features
    * FFS added symbolic links, file locking, unrestricted file name lengths and user quotas

## What's Close on Disk?

- Two enemies of closeness:
    1. Lateral movement, or seek times: this is major
    2. Rotational movement or delay: this is minor

## Seek Planning: Cylinder Groups

- Cylinder group: all of the data that can be read on the disk without moving the head
    * Comes from multiple platters
- On FFS each cylinder group has:
    * A backup copy of the superblock
    * A cylinder-specific header with superblock-like statistics
    * A number of inodes
    * Data blocks
    * It's almost like its own file system!

## Rotational Planning

- FFS superblock contained detailed disk geometry information allowing FFS to attempt to perform better block placement
- Example:
    * Imagine speed at which heads can read info off disk is greater than speed at which disk can return data to OS
    * So disk cannot read consecutive blocks off disk because after finishing transferring block 0 the heads are over a different block
    * FFS will incorporate this delay and attempt to lay out consecutive blocks for a single file as 0, 3, 6, 9, etc

## Back to the Future

- Does this stuff matter anymore?
- If not, why not, and is it a good thing that it doesn't?

## Hardware vs Software

- Who should be responsible for making the slow disk fast?
    * Hardware: fixed and fast
    * Software: flexible and slow

## Put the OS in Control

- OS: Put this block exactly where I tell you to
- Disk: Yes I will
- Pros:
    * OS has better visibility into workloads, users, relationships, consistency requirements, etc
    * This info can improve performance
- Cons:
    * OS are slow and buggy

## Leave it to Hardware

- OS: Disk, here is some data. I trust you will do the right thing with it
- Disk: Okay I am clever
- Pros:
    * Devices knows much more about itself than OS can be expected to
    * Device buffers and caches are closer to the disk
- Cons:
    * Device opaqueness may violate guarantees that the OS is trying to provide

## FFS Continues to Improve

- Block sizing: continues to respond to changes to average file sizes
    * Small blocks: less internal frag, more seeks
    * Large blocks: more internal frag, less seeks
- Co-locating inodes and directories
    * Problem: accessing directory contents is slow
    * Solution: jam inodes for directory into directory file itself
- Separate solution to consistency called soft updates which has recently been combined with journaling