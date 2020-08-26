# Lecture 22

## File Systems to the Rescue

- Low-level disk interface is messy and very limited
    * Requires reading and writing entire 512-byte blocks
    * No notion of files, directories, etc
- File systems take this limited block-level device and create the file abstraction almost entirely in software
    * Compared to the CPU and memory that we have studied previously more of the file abstraction is implemented in software
    * This explains the plethora of available file systems: EXT2/3/4, reiserfs, ntfs, jfs, xfs, etc

## What About Flash

- No moving parts
- We can eliminate a lot of the complexity of modern file systems
- Except that:
    * Have to erase an entire large chunk before we can rewrite it
    * Wears out faster than magnetic drives, and can wear unevenly if we are not careful

## Clarifying the Concept of a File

- Most of us are familiar with files but the semantics of file have a variety of sources which are worth separating:
    * Just a file: minimum it takes to be a file
    * About a file: what other useful information do most file systems typically store about files
    * Files and porocesses: what additional properties does the UNIX file system interface introduce to allow user processes to manipulate files
    * Files together: given multiple files, how do we organize them in a useful way

## Just a File: The Minimum

- What does a file have to do to be useful:
    * Reliably store data
    * Be located usually via a name

## Basic File Expectations

- At minimum we expect that
    * File contents should not change unexpectedly
    * File contents should change when requested and as requested
- These requirements seem simple but many file systems do not meet them
- Failures such as power outages and sudden ejects make file system design difficult and exposed tradeoffs between durability and performance
    * Memory: fast, transient
    * Disk: slow, stable

## About a File: File Metadata

- What else might we want to know about a file:
    * When was the file created, last accessed, or last modified
    * Who is allowed to do what to the file e.g., read, write, rename, change other attributes, etc
    * Other file attributes?

## Where to Store File Metadata

- MP3 file contains audio data but also has title, artist, date
- Where should these attributes be stored:
    * In the file itself
    * In another file
    * In attributes associated with the file maintained by the file system
- In the file:
    * Ex) MP3 ID3 tag, data container stored within an MP3 file
    * Pro: travels with the file from computer to computer
    * Con: requires programs that access the file to understand the format of the embedded data
- In another file:
    * Ex) iTunes database
    * Pro: can be maintained separately by each application
    * Con: Does not move with the file and the separate file mnust be kept in sync when the files it stores info about changes
- In attributes:
    * Ex) attributes have been supported by a variety of file systems including BFS
    * Pro: maintained by the file system so can be queried quickly
    * Con: does not move with the file and creates compatability problems with other file systems

## Processes and Files: UNIX Semantics

- Many file systems provide an interface for establishing a relationship between a process and a file:
    * "I have a file open. I am using this file"
    * "I am finished using the file and will close it now"
- Why does the file system wabnt to establish these process-file relationships?
    * Can improve performance if the OS knows what files are actively being used by using caching or read-ahead
    * File system may provide guarantees to processes based on thie relationship e.g., exclusive access
    * Some file systems (particularly network file systems) don't even bother with establishing these relationships
- UNIX semantics simplify reads and writes to files by storing the file position for processes
    * This is a convenience, not a requirement: processes could be required to provide a position with every read and write
