# Lecture 23

## UNIX File Interface

- Establishing relationships:
    * `open("foo")`: I would like to use the file named `foo`
    * `close("foo")`: I am finished with `foo`
- Reading and writing:
    * `read(2)`: I would like to perform a read from file handle `2` at the current position
    * `write(2)`: I would like to perform a write from file handle `2` at the current position
- Positioning:
    * `lseek(2, 100)`: Please move my saved position for file handle `2` to position `100`

## Files Together: File Organization

- Each file has to have a unique name
- Flat name spaces were actually used by some early file systems but file naming got bad fast:
    * `letterToMom.txt`
    * `letterToSuzanna.txt`
    * `AnotherLetterToSuzanna.txt`
    * etc

## Hierarchical Implications

- Don't look at everything all at once, allow users to store and examine related files together:
    * `letters/Mom/Letter.txt`
    * `letters/Suzanna/Letters/1.txt`
    * `letters/Suzanna/Letters/2.txt`
    * etc
- Each file should be stored in one place

## Location Implications

- Location requires navigation and relative navigation is useful, meaning that locations (directories) can include pointers to other locations (other directories)
- Finally location is only meaningful if it is tied to a files name so hierarchical file systems implement name spaces, which require that a file's name map to a single unique location within the file system

## Why Trees

- File systems usually require that files be organized into an acyclic graph with a single root also known as a tree
- Why?
    * Trees produce a single canonical name for each file on the system as well as an infinite number of relative names
        + Canonical name: `/you/used/to/love/well`
        + Relative name: `/you/used/to/love/me/../well`

## File System Design Goals

1. Efficiently translate file names to file contents
2. Allow files to move, grow, shrink, and otherwise change
3. Optimize access to single files
4. Optimize access to multiple files, particularly related files
5. Survive failures and maintain a consistent view of file names and contents

## Three of These Things Are All Like Each Other

- The file systems we will discuss all support the following features:
    * Files, including some number of file attributes and permissions
    * Names, organized into a hierarchical name space
- This is the file interface and feature set we are all used to
- The difference lie in the implementation and what happens on disk

## Implementing Hierarchical File Systems

- Broadly speaking, two types of disk blocks:
    1. Data blocks: contain file data
    2. Index nodes (inodes): contain not file data
- What makes file systems different:
    * On-disk layout: how does file system decide where to put data and metadata blocks in order to optimize file access
    * Data structures: what data structures does the filesystem use to translate names and locate file data
    * Crash recovery: how does the file system prepare for and recover from crashes

## File System Challenges

- File systems are really maintaining a large and complex data structure using disk blocks as storage
- This is hard because making changes potentially requires updating many different structures

## Example write

- Say a process wants to `write` data to the end of a file. What does a file system have to do?
    1. Find empty disk blocks to use and mark them as in use
    2. Associate those blocks with the file that is being written to
    3. Adjust the size of the file that is being written to
    4. Actually copy the data to the disk blocks being used
- From perspective of a process all of these things need to happen synchronously
- In reality, many different asynchrounous operations are involved touching many different disk blocks
- This creates both a consistency and a performance problem

## What Happens on Disk?

- Let's consider the on-disk structures used by modern file systems
- Specifically we are going to investigate how file systems:
    * Translate paths to file index nodes or inodes
    * Find data blocks associated with a given inode (file)
    * Allocate and free inodes and data blocks
- We will ty and keep this high level but examples used are drawn from `ext4` file system

## Sectors, Blocks and Extents

- Sector: smallest unit that the disk allows to be written (typically 256 bytes)
- Block: smallest unit that the filesystem actually writes (usually 4k bytes)
- Extent: set of contiguous blocks used to hold part of a file (described by start and end block)
- Why would file systems not write chunks smaller than 4k?
    * Because contiguous writes are good for disk head scheduling and 4k is the page size which affects in-memory file caching
- Why would file systems want to write file data in even larger chunks?
    * Because contiguous writes are good for disk head scheduling and many files are larger than 4k

## ext4 inodes

- 1 inode per file
- 256 bytes so 1 per sector or 16 per block
- Contains:
    * Location of file data blocks (contents)
    * Permissions including user, read/write/execute bits, etc
    * Timestamps including creation (`crtime`), access (`atime`), content modification (`mtime`), attribute modification (`ctime`) and delete (`dtime`) times
    * Named and located by number

## Locating Inodes

- How does the system translate an inode number into an inode structure?
    * All inodes are created at hofrmat time at well-known locations
- What are the consequences of this?
    * Inodes may not be located near file contents
        + `ext4` creates multiple blocks of inodes within the drive to reduce seek times between inodes and data
    * Fixed number of inodes for the file system
        + Can run out of inodes before we run out of data blocks
        + `ext4` creates approximately one inode per 16kb of data blocks, but this can be configured at format time

## Directories

- Simply a special file the contents of which map inode numbers to relative names
