# Lecture 28

## Introduction to Messaage Queues

- Message queues can be used to pass messages between related or unrelated processes executing on the same machine
    * Message queues are similar to pipes and fifos (named pipes) but differ in two aspects:
        1. Message boudnaries are preserved so reads and writers communicate in units of messages
        2. Message queues are kernel persistent
- Message queue can be thought of as a linked list of messages in the kernel space
    * Processes with adequate permissions can puyt messages onto the queue and processes with adequate permissions can remove messages from the queue

# Differences between FIFOs and Message Queues

- Message queues have kernel perisstence while FIFOs have process persistence
- In pipes, process read or write stream of bytes while in message queues a process read or write a complete delimited message
    * Not possible to read a partial message leaving rest behind in IPC object
- In pipes, a write makes no sense unless a reader also exists
    * In message queues there is no requirement that some reader must be waiting before a process writes a message to the queue
- Message queues are priority driven
    * Queue always resmains sorted with oldest message of highest priority at the front
- A process can determine status of a message queue

## System-V vs POSIX Message Queues

- Three IPC mechanisms (message queues, semaphores and shared memory) are collectively referred to as either System-V IPC or POSIX IPC
    * Both System-V as well as POSIX standard provides API for implementation of these IPC mechanism
    * The two major differences between these two implementations for message queues are:
        1. System-V message queues can return a message of any desired priority while POSIX message queue always return the oldest message of highest priority
        2. POSIX message queues allow the generation of signal when a message is placed onto an empty queue where as nothing similar is probvided by System-V message queue
- System-V API
    * Header file: `sys/msg.h`
    * Data structure: `msqid_ds`
    * Create/open: `msgget()`
    * Close: none
    * Perform IPC: `msgsnd()`, `msgrvc()`
    * Control operations: `msgctl()`

## Creating or opening a message queue

- `int msgget(key_t key, int msgflag);`
- To create a new message queue or to get the identifier of an existing queue we use `msgget()` system call which on success returns a unique message queue identifier
- If message queue associated with first argument, `key` already exists, the call returns the identifier of the existing message queue
    * Otherwise it creates a new message queue
- We can use `IPC_PRIVATE` constant as the first argument
    * Parent process creates message queue prior to performing a `fork()` and child inherits the returned message queue identifier
    * For unrelated processes we can use this contant but in that case creator process has to write the returned message queue identifier in a file that can be read by other process
    * Second argument `msgflag` is normally `IPC_CREAT|0666`

## Sending messages

- `int msgsnd(int msqid, const void* msgp, size_t msgsz, int msgflg);`
- `msgsnd()` system call is used to send a message to the message queue identified by its first argument which is the message queue identifier
- Second argument is a pointer to a structure of type `msgbuf` having two fields:
```
struct msgbuf{
    long mtype;
    char mtext[512];
}
```
- Third argument `msgsz` is the size of `mtext` field
- Fourth argument `msgflag` can be `0` or `IPC_NOWAIT`

## Receive messages

- `int msgrcv(int msqid, void* msgp, size_t maxmsgsz, long msgtype, int msgflag);`
- `msgrcv()` system call reads and removes a message from message queue identified by its first argument `msqid` and copies its contents into the buffer pointed to by its second argument `msgp`
- Third argument `maxmsgsz` specifies max space available in `mtext` field
- Fifth argument `msgflg` is a bit mask normally kept as `IPC_NOWAIT`
- Fourth argument `msgtype` is used to specify which message is to be removed and returned to the caller based
    * Achieved by specifying the `msgtype` field of the `struct msgbuf`
    * `0`: first message from queue is removed and returned
    * `>0`: first message whose `mtype` field equals `msgtype` is removed and returned
    * `<0`: first message of the lowest `mtype` field less than or equal to absolute value of `msgtype` is removed and returned
- Example:
    * Consider this message queue
        1. msgtype = 300
        2. msgtype = 100
        3. msgtype = 200
        4. msgtype = 400
        5. msgtype = 100
    * `msgrcv(id,&msg,maxmsgsz,0,0)` would return 1, 2, 3, 4, 5
    * `msgrcv(id,&msg,maxmsgsz,100,0)` would return 2, 5
    * `msgrcv(id,&msg,maxmsgsz,-300,0)` would return 2, 5, 3, 1

## Message queue as linked list in kernel

Consider the following scenario:
1. Process calls `msgget()` to create a new message queue
    * This creates an entry into the kernel Message Table
2. Process calls `msgsnd()` to send a message into the newly created queue
    * This makes the entry in the kernel Message Table from step 1 point to the newly created Message Record which contains:
        + Next pointer (currently pointing to Null)
        + mtype
        + msg size
        + kernel pointer (points to area in Kernel data area containing the message)
3. Process calls `msgsnd()` to create another message in the newly created queue
    * This causes the Message Record from step 2 to point to the newly created message using it's next pointer
    * Newly created message now has its next pointer pointing to null and its kernel pointer pointing to another area in the kernel data area that contains its data
    * It's metadata (mtype, msg size) are also filled in the Message Record
4. Process terminates
    * Even after process terminates in the User Space the Message Queue persists in the kernel
5. Now some other process calls `msgget()` with same key value in order to get the identifier of the previously created message queue
6. Process then calls `msgrcv()` with the identifier
    * Kernel copies the message data from kernel data area to the process's virtual address space
    * Then it deletes the message from kernel space
7. Receiver process terminates and the message queue still persists

## Example

- `/proc/sys/kernel/msgmni` to see min msg queue length
- `/proc/sys/kernel/msgmax` to see max msg queue length
- Example of sender:
```
#include <stdio.h>
#include <sys/msg.h>
#include <sys/ipc.h>
#include <stdlib.h>
#include <string.h>

#define SIZE 512
struct msgbuf{
   long mtype;
   char mtext[SIZE];
};
int main(){
   key_t key = ftok("./myfile", 65);
   int qid = msgget(key, IPC_CREAT | 0666);
//place first message on this message queue
   struct msgbuf msg1;
   msg1.mtype = 10;
   strcpy(msg1.mtext, "Learning is fun with Arif\n");
   msgsnd(qid, &msg1, sizeof msg1.mtext, 0);
//place second message on this message queue
   struct msgbuf msg2;
   msg2.mtype = 20;
   strcpy(msg2.mtext, "This is GR8\n");
   msgsnd(qid, &msg2, sizeof msg2.mtext, 0);
   return 0;
}
```
- Example of receiver:
```
#include <sys/msg.h>
#include <sys/ipc.h>
#include <stdlib.h>
#include <stdio.h>
#define SIZE 512
struct msgbuf{
   long mtype;
   char mtext[SIZE];
};
int main(){
   key_t key = ftok("./myfile", 65);
   int qid = msgget(key, IPC_CREAT | 0666);
//get the first message from the message queue
   struct msgbuf msg;
   msgrcv(qid, &msg, SIZE, 0, IPC_NOWAIT);
   printf("Message Received: %s\n",msg.mtext);
   return 0;
}
```
- `ipcs -q` shows current message queues on system including message queue id
- `ipcrm -q <message queue id>` to remove message queue