# Lecture 29

## Introduction to Shared Memory

- Shared memory allows 2+ processes to share a memory region or segment of memory for reading and writing purposes
- Problem with pipes, fifo and message queue is that mode switches are involved as the data has to pass from one process buffer to the kernel buffer and then to another process buffer
- Since access to user-space memory does not require a mode switch, shared memory is considered as one of the quickest means of IPC

## APIs to shared memory

- System-V API
    * Header file: `sys/shm.h`
    * Data structure: `shmid_ds`
    * Create/open: `shmget()`, `sgmat()`
    * Close: `shmdet()`
    * Perform IPC: Access memory
    * Control options: `shmctl()`

## Creating/Opening Shared Memory Segment

- `int shmget(key_t key, size_t size, int shmflg);`
- `shmget()` system call creates a new shared memory segm,ent or obtains the identifier of an existing segment
    * Contents of a newly created shared memory segment are initialized to `0`
    * Return value is ID of the shared memory segment
- First argument `key` can be the constant `IPC_PRIVATE` or can be achieved using `ftok()` library call
- Second argument `size` specifies the desired size of the segment in bytes
    * Kernel round it up to next multiple of the system page size
    * If we use `shmget()` to obtain the identifier of an existing segment then size has no effecct on the segment
- `shmflg` argument specifies permissions to be placed on a new shared memory segment or checked against an existing segment
    * In addition, it can be a bitwise OR of contants like `IPC_CREAT` and `IPC_EXCL`

## Using shared memory segment

- `shmat()` system call attaches shared memory segment identified by `shmid` to address space of calling process
- Second argument `shmaddr` is the address where the memory sengment will be attached
    * If we want OS kernel to select a suitable address, keep it NULL
- Third argument `shmflg` can be `SHM_RDONLY` to attach the shared memory segment for read-only access
    * We can place a zero over there for giving both read and write access
- On success `shmat()` returns the address at which the shared memory segment is attached which can be treated like a normal C pointer
    * We can assign the return value from `shmat()` to a pointer of some intrinsic data type or a programmer defined structure

## Detaching shared memory segment

- When process no longer needs to access shared memory segment, it can call `shmdt()` to detach segment from its address space
- The only argment to `shmaddr` identifies the segment to be detached
    * It should be a value returned by a previous call to `shmat()`
- Detaching a shared memory segment is not the same as deleting it
    * Deleting can be performed using `shmctl()`
- Child created by `fork()` inherits parent's attached shared memory segments
    * Thus shared memory provides an easy method of IPC between parent and child
    * However, after an `exec()` all attached shared memory segments are detached
- Shared memory segments are also automatically detached on process termination

## Delete shared memory segment

- `shmctl()` system call is used to perform control operations on the shared memory segment specified in its first argument `shmid`
- One of the basic control operation is deletion of the shared memory segment
    * This can be done by giving `IPC_RMID` as the `cmd` in the second argument
    * This will destory the memory segment after the last process detaches it
- For deletion operation of shared memory the third argument is kept NULL

## Example

- `cat /proc/sys/kernel/shmni` to see maximum limit of shared memory segments
- `cat /proc/sys/kernel/shmmax` to see maximum size of shared memory segments
- `ipcs -m` to view shared memory segments
- Example of writer:
```
#include <stdio.h>
#include <sys/shm.h>
#include <sys/ipc.h>
#include <sys/stat.h>
int main(){
// ftok to generate unique key
   key_t key = ftok("f1.txt", 65);
// shmget returns an identifier in shmid
   int shmid = shmget(key, 1024, 0666|IPC_CREAT);
// shmat to attach to shared memory
   char *buffer = (char*)shmat(shmid, NULL, 0);
   printf("Please enter a string to be written in shared memory:\n");
   fgets(buffer, 512, stdin);
   printf("\nData has been written in shared memory. Bye\n");
//detach from shared memory
   shmdt(buffer);
   return 0;
}
```
- Example of reader:
```
#include <stdio.h>
#include <sys/shm.h>
#include <sys/ipc.h>
#include <sys/stat.h>
int main(){
// ftok to generate unique key
   key_t key = ftok("f1.txt", 65);
// shmget returns an identifier of existing shared memory
   int shmid = shmget(key, 1024, 0666|IPC_CREAT);
// shmat to attach to shared memory
   char *buffer = (char*)shmat(shmid, NULL, 0);
   printf("Data read from memory: %s\n", buffer);
//detach from shared memory
   shmdt(buffer);
// destroy the shared memory
//   shmctl(shmid, IPC_RMID, NULL);
   return 0;
}
```
