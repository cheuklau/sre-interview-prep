# Lecture 24

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
```
ls -i /
131073 bin
39217 boot
    3 dev
...
```
- Above shows inode mapping of each of its contents
- Note `/proc` and `/sys` has the same inode number `1` since they are pseudo files (does not live on disk)

## open: Path Name Translation

- `open("/etc/default/keyboard")` must translate `/etc/default/keyboard` into an inode number
    1. Get inode number for root directory (usually a fixed agreed on inode number e.g., `2`)
    2. Open directory with inode number `2` and look for `etc` Lets assume it is `393218`
    3. Open directory with inode number `393218` and look for `default`. Lets assume it is `393247`
    4. Open directory with inode number `393247` and look for `keyboard`. Lets assume it is `394692`
    5. Open file with inode number `394692`

## read/write: Retrieving and Modifying Data Blocks

- `read/write(filehandle, 345)` must tranlsate `345` (the offset) to a data block within the open file to determine what data block to modify
- There are multiple ways of doing this

## Data Blocks: Linked Lists

- One solution: organize data blocks into a linked list
    * Inode contains a pointer to the first data block
    * Each data block contains a pointer to the previous and next data block
- Pros:
    * Simple
    * Small amount of information in inode
- Cons:
    * Offset lookups are slow - O(n) in the size of the file

## Data Blocks: Flat Array

- Store all data blocks in the inode in a single array and allocate at file creation time
- Pros:
    * Simple
    * Offset lookups are fast O(1)
- Cons:
    * Small file size fixed at startup time

## Data Blocks: Multilevel Index

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