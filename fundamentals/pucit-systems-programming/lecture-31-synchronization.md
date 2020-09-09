# Lecture 31

## Overview of Synchronization

- Synchronization refers to relationships among events
- There are two constraints of synchronization
    1. Serialization: event A must happen before event B
    2. Mutual exclusion: Event A and B must not happen at the same time
- In multi-threaded programs, programmer has no control over when a thread runs (scheduler makes this decision)
- Cocurrent programs are often non-deterministic which means it is not possible to tell by looking at the program what will happen when it will execute
- Concurrent access to shared data may result in data inconsistency so we need to apply some concurrency control mechanism using which multiple threads can access shared data without any conflict

## Example: Deposit and withdrawal

- Consider bank account with balance of 100
- Deposit process deposits 25 thus updating balance to 125
- Witdrawal runs and withdraws 10
- Thus updating balance of account to 115
- Instruction that updates the balance varaible can be written in assembly:
    * For deposit process:
    ```
    D1: MOV R1, balance
    D2: ADD R1, deposit_amt
    D3: MOV balance, R1
    ```
    * For withdrawal
    ```
    W1: MOV R2, balance
    W2: SUB R2, wdr_amt
    W3: MOV balance, R2
    ```
- Suppose both processes run concurrently:
    * Scenario 1: D1, D2, D3, W1, W2, W3: Balance = 115
    * Scenario 2: D1, D2, W1, W2, D3, W3: Balance = 90
- Above illustrates a race condition
- Example of race condition:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
long balance = 0;//global variable
void * inc(void * arg);
void * dec(void * arg);
int main(){
   pthread_t t1, t2;
   pthread_create(&t1, NULL, inc,NULL);
   pthread_create(&t2, NULL, dec,NULL);
   pthread_join(t1,NULL);
   pthread_join(t2,NULL);
   printf("Value of balance is :%ld\n", balance);
   return 0;
}
void * inc(void * arg){
   for(long i=0;i<100000000;i++)
      balance++;
   pthread_exit(NULL);
}
void * dec(void * arg){
   for(long j=0;j<100000000;j++)
      balance--;
   pthread_exit(NULL);
}
```
- Example
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
int wordcount = 0;
void* f1(void * arg);
int main(int argc, char* argv[]){
   if(argc != 3){
      printf("Invalid number of arguments. Must pass two file names.\n");
      exit(1);
   }
   pthread_t tid1, tid2;
   pthread_create(&tid1, NULL, f1, (void*)argv[1]);
   pthread_create(&tid2, NULL, f1, (void*)argv[2]);
   pthread_join(tid1, NULL);
   pthread_join(tid2, NULL);
   printf("Number of characters in both files: %d\n", wordcount);
   return 0;
}
void* f1(void* args){
   char* filename = (char*)args;
   char ch;
   int fd = open(filename, O_RDONLY);
   while((read(fd, &ch, 1)) != 0){
	   wordcount++;
   }
   close(fd);
   pthread_exit(NULL);
}
```

## Data Sharing Among Threads

- Normally modifying an object requires several steps
    * While these steps are being carried out the object is typically not in a wwell formed state
    * If anothger thread tries to access the object during that time it will likely get a corrupt information
    * The entire program might have undefined behavior afterwards
    * What data is shared?
        1. Global data and static local data
            * Case of static local data is only significant if two or more threads execute the function containining static local variable at the same time
        2. Dynamically allocated data (in heap) that has had its address put into a global/static variable
        3. Data members of a class object that has two or more of tis member functions called by different threads at the same time
    * What data is not shared:
        1. Local variables
            * Even if two threads call the same function they will have differnt copies of the local variable in that function
            * This is because local variables are kept on stack and every thread has its own stack
        2. Function parameters are not shared
            * Parameters of function are also put on the stack and thus every thread will have its own copy of those as well
- Example:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
char** ptr;
void * thread_function(void * localarg);
int main(){
   pthread_t tid[2];
   char* msg[2] = {"Hello from Arif", "Hello from PUCIT"};
   ptr = msg;
   for(int i=0;i<2;i++){
      pthread_create(&tid[i], NULL, thread_function, (void*)&i);
      pthread_join(tid[i], NULL);
   }
   return 0;
}
void * thread_function(void * localarg){
   int myid = *((int*)localarg);
   // Shared
   static int svar = 0;
   printf("[%d]: %s (svar = %d)\n", myid, ptr[myid], ++svar);
   pthread_exit(NULL);
}
```

## Thread safe vs reentrant functions

- A thread safe function can be called simultaneously from multiple threads even when invocations use shared data
    * this is becvause each thread accesses shared data using some concurrentcy control mechanism
- A reentrant function can also be called simulataneously from multiple threads but only if each invocation uses its own data
- Therefore a thread-safe function is always reentrant but a reentrant function is not always thread safe

## Four classes of thread unsafe functions

1. Failing to protect shared variables (solution: use locks to protect shared variables)
2. Relying on persistent state across invocation (do not use)
3. Returning a pointer to a static variable (do not use)
4. Callling a thread unsafe function (solution: call thread safe or re-entrant versions of functions)

## What is Mutex?

- Mutex is MUTual EXclusion device and is useful for protecting shared data structures from concurrent modifications and implementing critical sections
- Mutex has two possible states:
    1. Unlocked (not owned by any thread)
    2. Locked (owned by one thread)
- It can never be owned by two different threads simulataneously
- Thread attempting to lock a mutex that is already locked by another thread is suspecnded until the owner thread unlocks the mutex
- Linux guarantees that race condition do not occur among threads attempting to lock a mutex
- How to use a mutex:
    1. Create and initialize a mutex variable
    2. Several threads attempt to lock the mutex
    3. Only one thread succeeds and owns the mutex
    4. Owner thread carry out operations on shared data
    5. Owner thread unlocks the mutex
    6. Another thread acquires mutex and repeats the process
    7. Mutex is destroyed
- Mutex initialization
    * Static initialization
        * Default mutex attributes are appropriate, use the following macro: `pthread_mutex_t mut = PTHREAD_MUTEX_INITIALIZER;`
    * Run time initialization
        * Dynamically initialize the mutex using `pthread_mutex_init()`
        * Function initalizes the mutex object pointed to by `mptr` according to the mutex attributes specified in `attr`
- Locking, unlocking and destorying mutex
    * `lock()` will lock the `pthread_mutex_t` object referenced by `mptr`
        + If mutex is already locked the calling thread blocks until mutex is unlocked
    * `trylock()` similar to lock expcet that if mutex object is currently locked, the call returns immediately with error code `EBUSY`
    * `unlock()` call releases the mutex object
        + Manner in which a mutex is released is dependent on th emutex's attribute type
        + If there are threads blocked on the mutex object when `unlock()` is called, the scheduling policy shall determine which thread shall acquire the mutex
    * `detroy()` call destroys the mutex object

## Mutex Dead Locks

- Be sure to observe following points to avoid dead locks while using mutexes:
    1. No thread should attempt to lock or unlock a mutex that has not been initialized
    2. Only the owner thread of the mutex should lock it
    3. Do not lock a mutex already locked
    4. Do not unlock a mutex that is not locked
    5. Do not destroy a locked mutex

## Examples

- Example solving previous race condition using mutex:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
long balance = 0;//global variable
void * inc(void * arg);
void * dec(void * arg);
pthread_mutex_t mut = PTHREAD_MUTEX_INITIALIZER;
int main(){
   pthread_t t1, t2;
   pthread_create(&t1, NULL, inc,NULL);
   pthread_create(&t2, NULL, dec,NULL);
   pthread_join(t1,NULL);
   pthread_join(t2,NULL);
   printf("Value of balance is :%ld\n", balance);
   return 0;
}
void * inc(void * arg){
   for(long i=0;i<100000000;i++){
       // Lock and unlock around the critical section changing the balance
      pthread_mutex_lock(&mut);
      balance++;
      pthread_mutex_unlock(&mut);
   }
   pthread_exit(NULL);
}
void * dec(void * arg){
   for(long j=0;j<100000000;j++){
    // Lock and unlock around the critical section changing the balance
      pthread_mutex_lock(&mut);
      balance--;
      pthread_mutex_unlock(&mut);
    }
   pthread_exit(NULL);
}
```
- Example
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
int wordcount = 0;
pthread_mutex_t mut;
void* f1(void * arg);
int main(int argc, char* argv[]){
   if(argc != 3){
      printf("Must pass two file names.\n");
      exit(1);
   }
   pthread_mutex_init(&mut,NULL);
   pthread_t tid1, tid2;
   pthread_create(&tid1, NULL, f1, (void*)argv[1]);
   pthread_create(&tid2, NULL, f1, (void*)argv[2]);
   pthread_join(tid1, NULL);
   pthread_join(tid2, NULL);
   printf("Number of characters in both files: %d\n", wordcount);
   return 0;
}
void* f1(void* args){
   char* filename = (char*)args;
   char ch;
   int fd = open(filename, O_RDONLY);
   while((read(fd, &ch, 1)) != 0){
       // Lock and unlock around critical section
      pthread_mutex_lock(&mut);
	   wordcount++;
      pthread_mutex_unlock(&mut);
   }
   close(fd);
   pthread_exit(NULL);
}
```

## Mutex attributes

- `PTHREAD_MUTEX_ININTIALIZER` (fast mutex)
    * Locking an already locked mutex results in suspending the calling thread
    * Unlocking an already unlocked mutex results in undefined behavior
    * Unlocking a mutex that is not locked by calling thread results in undefined behavior
- `PTHREAD_ERRORCHECK_MUTEX_INITIALIZER_NP` (error checking mutex)
    * Locking an already locked mutex returns immediately with `EDEADLK`
    * Unlocking an already unlocked mutex returns an error
    * Unlocking a mutex that is not locked by calling thread returns an error

## Example

- Example:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
void * f1(void * arg);
pthread_mutex_t mut;
int main(){
   pthread_mutex_init(&mut, NULL);
   pthread_t t1;
   pthread_create(&t1, NULL, f1,NULL);
   pthread_join(t1,NULL);
   printf("Bye Bye from main\n");
   return 0;
}
void * f1(void * arg){
   pthread_mutex_lock(&mut);
   pthread_mutex_lock(&mut);
   printf("Locking an already locked error checking mutex returns with error\n");
   pthread_mutex_unlock(&mut);
   pthread_exit(NULL);
}
```

## Condition Variables

- Producer-consumer problem
    * Producer produces info consumed by consumer process
    * To allow producer and consumer to run concurrently we must have a buffer that can be efilled by produced and emptied by consumer
    * Buffer can be bounded or unbounded
        1. Bounded buffer: places no limit on the size of the buffer; consumer may have to wait for new items if buffer is empty but producer can always produce new items
        2. Bounded buffer: assumes fixed size buffer; consumer must wait if buffer is empty and producer must wait if buffer is fulil
    * While an item is being added or removerd by buffer, buffer is in inconsistent state
        + Threads must have exclusive access to the buffer
        + If a consumer thread arrives while buffer is empty, it blocks until a producer adds a new item
    * Implicit synchorinzation
        + `grep prog1.c | wc -1`
        + `grep` is a producer and `wc` is the consumer
        + `grep` writes into pipe and `wc` reads from pipe
        + Required synchronization is handled implicity by the kernel
        + If producer gets ahead of consumer, kernel puts the producer to sleep when it calls `write()` until more room available in the pipe
        + If consumer gets ahead of producer, kernel puts consumer to sleep with it calls `read()` until some data is in the pipe
    * Explicit synchronization
        + When we as programmers are using some shared memory/data structure, we use some form of IPC between priducer and consumer for data transfer
        + We need to ensure that some type of explicit synchronization is performed between producer and consumer
- Solution to such problems like the producer-consumer are condition variables
    * Condition variable is a synchronization construct that allows threads to suspend execution and relinquish the processors until some condition is satisfied
    * The two basic operations of condition variables are:
        1. `signal()`: wake up a sleeping thread on this condition
        2. `wait()`: release lock, go to sleep, reacquire lock after you are worken up
    * We say that a condition variable enable a thread to sleep inside a critical section
    * Any lock held by the thread is automatically released when the thread is put to sleep
    * Mutex is for locking and condition variable is for waiting

## Initializing pthread_cond_t variable

- Static initialization
    * Case where default attributes are appropriate we can use `pthread_cond_t cond = PTHREAD_COND_INITIALIZER;`
- Run time initlization
    * Case where we must dynamically initialize the condition variable using `pthread_cond_init()`
    * Initializes the condition variable obejct pointed to by the `cond` using the conditions specified in `attr`

## Operations on pthread_cond_t variable

- `pthread_cond_signal()` restarts one of the threads that are waiting on the condition variable `cond`
    * If no threads are waiting on `cond` nothing happens
    * If several threads are waiting on `cond` exactly one istarted but it is not specified which
- `pthread_cond_wait()` atomically unlocks its second argument `mutex` and waits for the condition variable `cond` to be signaled by suspending its execution

## Example

- Consumer thread
```
pthread_mutex_lock(&mut);
while(buffercount == 0)
    pthread_cond_wait(&empty, &mut);
// modify the buffer
pthread_mutex_unlock(&mut);
```
- Producer thread
```
pthread_mutex_lock(&mut);
// modify the buffer
if(buffer == 1)
    pthread_cond_signal(&emptry);
pthread_mutex_unlock(&mut);
```
