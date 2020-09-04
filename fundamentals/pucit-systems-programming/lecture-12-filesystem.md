# Lecture 12

## Recap of OS Lectures in another course

- Hard disk geometry
    * How data is written/read on disk platter of magnetic hard disk
    * Read/write heads, tracks, sectors and cylinders
- Partitioning a hard disk
    * Divide disk into logical parts for better organization of data
    * Formatting each partition with a filesystem e.g., ext4
    * Partition table is used to manage info about different partitions on a hard disk
    * Two most popular partition tables are MBR (master boot record), GPT (globally unique identifier partition table)
    * `fdisk` partitioning tool
- Formatting a hard disk
    * After making a partition, need to create a file system on it
    * FS provides an abstraction to user to organize files without working knowledge of underlying hardware
    * Common ones are ext2, ext4, vfat, etc
    * Different Max file size, partition size it supports, supports journaling
    * `mkfs`, `lsblk` commands used to format a hard disk
- Mounting a file system
    * Root file system mounted at system boot
    * Mount point can be any directory under the root file system (makes it look like part of the main tree)
    * `mount` and `umount` used for this
- File system architecture
    * Recapped in this lecture

## Schematic Structure of a Unix File System

- Consider the following linear view of your hard disk:
    * Master boot record partitioning scheme placed at 0 sector
        + Initial 446 bytes containing the stage 1 boot loader
        + 64 byte block containing the partition table
            - 16 byte entry of each of the four primary partitions
        + Last two bytes contain the disk signature
    * Partition 1
        + Boot block
            - Contains stage 2 boot loader if it is a bootable partition and has an operating system installed on it
        + Super block
            - Important information of partition
                * File system type
                * Data block size
                * Total number of blocks
                * Info about free and allocated blocks
        + Inode blocks
            - Every file on hard disk has an associated inode block containing metadata about a file:
                * Owner
                * Group
                * Type
                * Permissions
                * Time
                * Address: pointer that points to data blocks of this file
        + Data blocks
            - Actually contains file's data
            - Pointed to by inode blocks
    * Partition 2
    * Partition 3
    * Partition 4

## Structure of Unix Inode

- Consider the following linear view of a Unix inode:
    * Metadata
        + mode
        + owners
        + timestamps
        + size block count
        + direct blocks
            * Contains multiple pointers to data blocks for individual files
        + single indirect
        + double indirect
        + triple indirect
        + Note: single, double and triple indirect used for large files that can be made of multiple data blocks

## File system in practice (creating a file)

- `echo "This is text" 1> /home/arif/f1.txt`
- What happens when we type the above command:
    1. Searches for a free inode block e.g., `47`
    2. File metadata stored in inode block
        + Owner who executed command
        + Group of owner
        + Time stamps
        + File size
        + Permissions
    3. Kernel searches for one or more data blocks to store data; small text, but lets assume it occupies three data blocks:
        1. data block `150`
        2. data block `600`
        3. data block `700`
    4. kernel stores addresses of those three blocks into the inode block of `47`
    5. Kernel adds entry of the file into the appropraite directory `/home/arif` now has inode `47` with corresponding `f1.txt`
        * Directory is special kind of file maintained by the kernel
        * Contains just entries in it
        * Mapping of name and inode number
        * Writing a directory means creating or deleting entries from it
        * Reading means listing contents of directory

## Understanding directories

- Consider directory `demodir` with file named `y` and two subdirectories `a` and `c`
- `a` subdirectory has file `x`
- `c` subdirectory has file `x`
- `c` has two subdirectories `d1` and `d2` containing `hltox` and `copytox` files respectively
- `ls -iaR demodir/` results in:
```
demodir/:
2621457 . 2629351 .. 2627 a 267039 c 2627033 y

demodir/a:
2627038 . 2621457 .. 2627040 x

(and so on)
```

## Accessing a file

- `cat /home/arif/file1`
- What happens when we type the above command:
    1. Goes to the `root` directory (always inode `1`) and uses the direct block pointer to access the block `86` containing its file and directory mappings
    2. Inside of block `86`, the kernel looks up the inode belonging to the `home` directory (`6`)
    3. Kernel goes to inode `6` and uses the direct block pointer to access the block `190` containing `home` directory's file and directory mappings
    4. Inside of block `190`, the kernel looks up the inode belonging to the `arif` directory (`54`)
    5. Kernel goes to inode `54` and uses the direct block pointer to access the block `535` containing `arif` directory's file and directory mappings
    6. Inside block `535`, the kernel looks up the inode belonging to `file1` which corresponds to inode `32`
    7. Kernel goes to inode `32` and checks for permissions e.g., user ID vs file owner/group/others
        * Note: user must have execute permissions on directories and read permission on file itself
    8. Kernel goes to each data block one at a time, the first 10 block addresses are in the inode block, next in single, double and triple indirect blocks
        * Returns data to `cat` for printing data to standard output

## Connection of an opened file

- What happens when we open a file for reading or writing purpose:
    * How do we go from file descriptor to contents of file on a hard disk?
- Three structures involved:
    1. Process file descriptor table
        * Every process has a kernel maintained open file descriptor table
        * Max size is the max number of files that a process can open
        * Fields:
            + File descriptor flags
                - Example: Close on exit (close file when process makes an `exit()` system call)
            + File pointer
                - Points to entry in the System Wide File Table
    2. System Wide File Table
        * Kernel maintains one System Wide File Table for files opened by all processes in the system
        * Maximum number of entries is the max number of files OS can open at any time
        * Fields:
            1. File offset
                - Updated by read and write system calls
                - Normally starts at beginning of the file and as you read or write it moves ahead
            2. Status flags
                - Programmer normally specify when they open the file
                - read-only, write-only, read-write mode
                - all_trunc, all_exclusive, all_append, etc
            3. Inode pointer
                - Pointer to file of entry in inode table
    3. Inode table
        * Resides on the hard disk
        * Brought into memory from hard disk
        * Fields: described in previous section
            + Contains pointer to data block on disk
- Every process has three default file descriptors
    * 0 = standard input
    * 1 = standard output
    * 2 = standard error
- Note:
    * There is exactly one entry for each file in inode table
    * On the contrary, file descriptor table and system wide file table can have multiple entries for the same file on hard disk
    * Example, consider process that has opened a file twice
        + This results in two entries in the process file table
        + Both of those entries point to two separate entries in the system wide file table
        + Both of those entries in the system wide file table will point to the same inode in the inode table
    * Note: a process can also open a file twice with `dup()` system call
        + This results in two process file descriptor table entries, but they point to the same entry in the system wide file table
        + In this case both process uses the same offset
- If we have two processes that open the same file via `open()`
    + There will be two different entry, one for each process file descriptor table
    + Each will point to separate system wide file table entries
    + However, both system wide file table entries will point to the same inode
- If we have a process that opens a file by calling `open()` and later `fork()`
    + Child process inherits the file descriptor table of the parent process, so they point to the same system wide file table entry

## Universal I/O Model

- Four key system calls for performing file I/O (note that programming languages typically employ these calls indirectly via I/O libraries):
    1. `fd = open(pathname, flags, mode)`
        + Opens file identified by pathname
        + Returns a file descriptor used to refer to the open file in subsequent calls
        + If file does not exist then `open()` may create it depending on the settings of the flags bit-mask argument
        + Flaggs argument also specifies if file is to be opened for reading, writing or both
        + Mode arguemtn specifes the permissions to be placed on file if it is crated by this call
        + If `open()` not used to create a file, this argument is is ignored and can be ommitted
    2. `numread = read(fd, buffer, count)`
        + Reads at most count bytes from the open file referred to by fd and stores them in a buffer
        + `read()` call return number of bytes actually read
        + If no futher bytes could be read (i.e., EOF), `read()` returns 0
    3. `numwritten = write(fd, buffer, count)`
        + Writes up to count bytes from buffer to the open file referred to by fd
        + `write()` call returns the number of bytes actually written which may be less than count
    4. `status = close(fd)`
        + Called after I/O has been completed in order to release the file descriptor fd and its associated kernel resources