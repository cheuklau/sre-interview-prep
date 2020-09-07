# Lecture 23

## Sequential Programming

- Assume we want to add eight numbers
- If done sequentially, it will take 7 CPU cycles
- If we have four CPUs, the seven addition operatioons can be completed in just three CPU cycles by dividing the task among different CPUs

## Ways to Achieve Concurrency

- Multiple single threaded processes
    * Use `fork()` to create new process for handling every new task
        + Child process serves the client process while parent listens to new request
        + Possible only if each slave can operate in isolation
        + Need IPC between processes
        + Lots of memoory and time requireed for process creation
- Multiple threads within a single process
    * Create multiple threads within a single process
    * Goood if each slave need to share data
    * Cost of creating threads is low, and no IPC required
- Single process multiple events
    * Use non-blocking or asynchronuos I/O using `select()` and `poll()` system calls

## Overview of Threads

- Every process has two characteristics:
    1. Resource ownership: process includes virtual address space to hold process image
    2. Scheduling: follows an execution path that may be interleaved with other processes
- These twoo characteristics treated independently by the OS
- The unit of resource ownership is referred to as a process while the unit of dispathing is referred to as a thread
- Thread is an execution context that is independently shceduled but shares a single address space with other threads of the same process
- Similarities between proocesses and threads:
    * Like a process, thread can also be in one of many states (new, ready, running, block, terminated)
    * Only one thread can be in running state (single CPU)
    * Like a process a thread can create a child thread
- Differences betwen proocesses and threads:
    * Noo automatic protection in threads
    * Every process has its own address space while all other threads within a process executes within the same address space
- Each thread has its oown register and stack inside the processes virtual memory
- Consider pictorial view of a multi-threaded process (from top to bottom of process's virtual address space):
    * arg, env
    * stack for main thread growing down
    * stack for thread 3
    * stack for thread 2
    * stack for thread 1
    * shared libraries, shared memory
    * empty
    * heap growing up
    * unitialized data (`bss`)
    * initialized data
    * Text (program code)
        + thread 3 executing here
        + main thread executing here
        + thread 1 executing here
        + thread 2 executing here
        + note: each stack has its own program pointer to track where in code thread is running
- Threads within a process share:
    * PID, PPID, PGID, SID, UID, GID
    * Code and data sections
    * Global variables
    * Open files via PPFDT
    * Signal handlers
    * Interval timers
    * CPU time
    * Resources consumed
    * Nice value
    * Record locks (created using `fcntl()`)
- Threads have their own:
    * Thread ID
    * CPU context (PC and other registers)
    * Stack
    * State
    * errno variable
    * Priority
    * CPU affinity
    * Signal mask

## Thread Implementation Models

- Many to one `M:1` threading implementation
    * All of the details fo thread creation, termination, scheduling, synchronization and so on are handled entirely in user-space
    * Kernel knows nothing about existence of multiple threads within the process
    * Advantages
        1. Thread operations are fast as noo mode switch require
        2. User level threads can be used even if underlying platform does not support multithreading
    * Disadvantages
        1. When user level thread makes a blocking system call e.g., `read()` the entire process is blocked
        2. Since kernel is unaware of the existence of multiple threads within the process, it cannot schedule separate threads to different CPUs on multiprocessor hardnware
- one to one (1:1) threading implementation
    * Each thread maps onto a separate kernel scheduling entity (KSE)
    * All details of thread creation, termination, scheduling, synchronization and so on are handled by system calls inside the kernel
    * Advantages
        1. When kernel-level thread makes a blocking call e.g., `read()` only that thread is blocked
        2. Since kernel is aware of existence of multiple threads within same process, it can schedule separate threads to different CPUs on multiprocessor hardware
    * Disadvantages
        1. Thread operations are slow as a switch into the kernel mode is required
        2. Overhead of maintaining a separate KSE for each of the threads in an application place a significant load on the kernel scheduler, degrading overall system performance
- many-to-many (M:N) threading implementation
    * Combines advantages of 1:1 and M:1 models while eliminating disadvantages
    * Each process can have multiple associates KSEs and several threads may map to each KSE
    * Disadvantages
        1. Major disadvantage is complexity
            * Task of thread scheduling is shared between kernel and user space threading library which must cooperate and communicate infromation with one another
    * Note: This model was rejected as it required too many changes to the kernel; Linux threading imoplementations LinuxThreads and NPTL employ 1:1 model

## Linux Implementation of POSIX Threads

- LinuxThreads
    * Original Linux threading implementation
    * LinuxThreads creates an additional manager thread that handles thread creation and termination
    * Threads are created using `clone()` function with flags:
        + `CLONE_VM` for threads too share virtual memory
        + `CLONE_FILES` for threads to share file descriptors
        + `CLOONE_FS` for threads to share file-system related infoormation
        + `CLONE_SIGHAND` for threads to share signal disposition
    * Deviations from specified behavior:
        1. `getpid()` treturns different values in each of the threads of a process
        2. `getppid()` returns PID of the manager thread
        3. If a thread creates a child using `fork()`, only the thread that created the child process can `wait()` for it
        4. If thread calls `exec()`, SUSv3 requires all other threads to be terminated; not true for LinuxThreads
        5. Threads don't share PGIDs and SIDs
        6. Threads don't share resource limits
        7. Some version of `ps()` show all threads in a proocess as separate items with distinct PIDs
        8. CPU time returned by `times()` and resource usage info returned by `getrusage()` are per thread
        9. Threads don't share nice value set by `serpriority()`
- Native POSIX Threads Library (NPTL)
    * Modern Linux threading implementation
    * Addresses shortcomings of LinuxThreads
    * Adheres more closely to SUSv3 specification
    * Apps that employ large nuber of threads scale much better using NPTL thatn LinuxThreads
    * NPTL threads does noot require an additional manager thread
    * Threads are created using `clone()` that specifies all the flags of LinuxThreads and more

## Pthreads API

- Pthread API defines a number of data types and should be used to ensure the portability of programs and mostly defined in `/usr/include/x86-linux-gnu/bits/pthreadtypes.h`
    * `pthread_t` to identify a thread
    * `pthread_attr_t` to identify a thread attribute object
    * `pthread_mutex_t` for mutex
    * `pthread_cond_t` used for condition variable
    * `pthread_spinlock_t` to identify spinlock
    * `pthread_rwlock_t` for tread-write lock
    * `pthread_barrier_t` to identify a barrier
- `int pthread_create(pthread_t *tid, const pthread_attr_t, *attr, void *(*start)(void *), void *arg);`
    * Used to start a new thread in the calling process
    * New thread starts executioon by invoking the start functioon which is 3rd argument in above function
    * On success TID of new thread is returned through 1st argument
    * 2nd argument specifies attributes of the newly created thread
    * 4th argument is the pointer of type vboid which points to the value to be passed to thread start function
- `void pthread_exit(void *status);`
    * Function terminates the calling thread
    * `status` is returned to some other thread in the calling process
    * Pointer `status` must not point to an object that is local t othe calling thread since that object disappears when thread terminates
    * Ways for a thread to terminate:
        1. Thread functioon calls `return`
        2. Thread function calls `pthread_exit()`
        3. Main thread returns or calls `exit()`
        4. Any sibling thread calls `exit()`
- `int pthread_join(pthread_t tid, void **retval);`
    * Any peer thread can wait for another thread to terminate by calling `pthread_join()` similar to `waitpid()`
    * Failing to do so will produce the thread equivalent of a zombie process
    * 1st argument is ID of thread for which calling thread wish to wait
        + Unfortunately we have no way to wait for any of our threads like `wait()`
    * 2nd arguement can be null if some peer thread is not interested in the return value of the new thread
        + Otherwise, it can be a double pointer which will point to the status argument of the `pthread_exit()`
- Example of sequential program:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
void f1();
void f2();
int main(){
   f1();
   f2();
   printf("\nBye Bye from main\n");
   return 0;
}

void f1(){
   for(int i=0; i<5; i++){
      printf("%s", "PUCIT");
      fflush(stdout);
      sleep(1);
   }
}
void f2(){
   for(int i=0; i<5; i++){
      printf("%s", "ARIF");
      fflush(stdout);
      sleep(1);
   }
}
```
- Example: multi-threaded of above program
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
void * f1(void *);
void * f2(void *);
int main(){
   pthread_t tid1, tid2;
//create two child threads and wait for their termination
   pthread_create(&tid1, NULL, f1, NULL);
   pthread_create(&tid2, NULL, f2, NULL);
   //
   pthread_join(tid1, NULL);
   pthread_join(tid2, NULL);
   printf("\nBye Bye from main thread\n");
   return 0;
}

void * f1(void * arg){
   for(int i=0; i<5; i++){
      printf("%s", "PUCIT");
      fflush(stdout);
      sleep(1);
   }
   pthread_exit(NULL);
}
void * f2(void * arg){
   for(int i=0; i<5; i++){
      printf("%s", "ARIF");
      fflush(stdout);
      sleep(1);
   }
   return NULL;
}
```
- Note that threads run concurrently so it should take half the time approximately
- Another example of concurrently running threads:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
extern int errno;
void * f1(void *);
void * f2(void *);
int main(){
   pthread_t tid1, tid2;
//create two child threads
   pthread_create(&tid1, NULL, f1, NULL);
   pthread_create(&tid2, NULL, f2, NULL);
//join the two child threads
   pthread_join(tid1, NULL);
   pthread_join(tid2, NULL);
   printf("\nBye Bye from main thread\n");
   return 0;
}

void * f1(void * arg){
//   for(int i=0; i<10000; i++)
		while(1)
      fprintf(stderr, "%c", 'X');
   pthread_exit(NULL);
}
void * f2(void * arg){
//   for(int i=0; i<8000; i++)
		while(1)
      fprintf(stderr, "%c", 'O');
   pthread_exit(NULL);
}
```
- Example passing argument to thread program
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
extern int errno;
void * f1(void *);
void * f2(void *);
int main(int argc, char* argv[]){
   int countofX = atoi(argv[1]);
   int countofO = atoi(argv[2]);
   pthread_t tid1, tid2;
//create the two child threads
// Last argumentt is used as argument by thread
   pthread_create(&tid1, NULL, f1, (void*)&countofX);
   pthread_create(&tid2, NULL, f2, (void*)&countofO);
//joing the two child threads
   pthread_join(tid1, NULL);
   pthread_join(tid2, NULL);
   printf("\nBye Bye from main thread\n");
   return 0;
}

void * f1(void * arg){
   int ctr = *((int*)arg);
   for(int i=0; i<ctr; i++)
      fprintf(stderr, "%c", 'X');
   pthread_exit(NULL);
}
void * f2(void * arg){
   int ctr = *((int*)arg);
   for(int i=0; i<ctr; i++)
      fprintf(stderr, "%c", 'O');
   pthread_exit(NULL);
}
```
- Example passing multiple arguments to thread program
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
struct mystruct{
   char character;
   int count;
};
void * f1(void *);

int main(){
   pthread_t tid1, tid2;
   struct mystruct t1_args;
   struct mystruct t2_args;
//create a child thread to print 1000 Xs
   t1_args.character = 'X';
   t1_args.count = 1000;
   pthread_create(&tid1, NULL, f1, (void*)&t1_args);
//create a child thread to print 800 Os
   t2_args.character = 'O';
   t2_args.count = 800;
   pthread_create(&tid2, NULL, f1, (void*)&t2_args);
//wait for the child threads to terminate
   pthread_join(tid1, NULL);
   pthread_join(tid2, NULL);

   printf("\nBye Bye from main thread.\n");
   return 0;
}

void * f1(void * args){
   struct mystruct p = *(struct mystruct*)args;
   for (int i = 0; i < p.count; i++)
      putc(p.character,stdout);
   pthread_exit(NULL);
}
```

## Returning Value from a Thread Function

- A thread function can return a pointer to its parent/calling thread and that can be received in 2nd argument oof `pthread_join()`
- Pointer returned by `pthread_exit()` must not point to an object that is local to the thread since that variablke is created in the local stack of the terminating thread function
- Making local variable static will also fail
- Suppose two threads run the same `thread_function()`, the second thread may write over the static variable with its own return value and return value written by first thread will also be overwritten
- Best solution is to create the variable too be returned in the heap instead of the stack
- Example of thread returning a value:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>  //exit
#include <math.h>
void* f1(void *);
int main(int argc, char* argv[]){
   if (argc != 3){
      printf("Invalid arguments. Pl enter two integers\n");
      exit(1);
   }
   int num1 = atoi(argv[1]);
   int num2 = atoi(argv[2]);
   pthread_t tid1, tid2;
   pthread_create(&tid1, NULL, f1, (void*)&num1);
   pthread_create(&tid2, NULL, f1, (void*)&num2);
   void* rv1, *rv2;
   pthread_join(tid1, &rv1);
   pthread_join(tid2, &rv2);
   long prime1 = *(long*)rv1;
   long prime2 = *(long*)rv2;
   printf("\nThe %dth prime number as returned by child thread is: %ld\n",num1,prime1);
printf("\nThe %dth prime number as returned by child thread is: %ld\n",num2,prime2);
   return 0;
}

void * f1(void * args){
   int n = *((int*)args);
   // Create on heap
   long *candidate = (long*)malloc(sizeof(long));
   *candidate = 2;
   while(1){
      long factor;
      int is_prime = 1;
      for (factor = 2; factor <= sqrt((*candidate)); ++factor){
         if((*candidate)%2 == 0)
            { is_prime = 0; break; }
         if((*candidate) % factor == 0)
            { is_prime = 0; break; }
      }//end of for loop
      if(is_prime == 1)
         n--;
      if(n == 0)
         pthread_exit((void*)(candidate));
      ++(*candidate);
   }//end of while loop
}
```
- `gcc rv1.c -lpthread -lm`
- Example:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

void* f1(void * arg);
int main(int argc, char* argv[]){
   if(argc != 3){
      printf("Invalid number of arguments. Must pass two file names.\n");
      exit(1);
   }
   pthread_t tid1, tid2;
   void *rv1, *rv2;
   pthread_create(&tid1, NULL, f1, (void*)argv[1]);
   pthread_create(&tid2, NULL, f1, (void*)argv[2]);
   pthread_join(tid1, &rv1);
   pthread_join(tid2, &rv2);
   int count1 = *((int*)rv1);
   int count2 = *((int*)rv2);
   printf("Characters in %s: %d\n", argv[1], count1);
   printf("Characters in %s: %d\n", argv[2], count2);
   return 0;
}
void* f1(void* args){
   char* filename = (char*)args;
   int *result = (int*)malloc(sizeof(int));
   *result = 0;
   char ch;
   int fd = open(filename, O_RDONLY);
   while((read(fd, &ch, 1)) != 0){
	   (*result)++;
   }
   close(fd);
   pthread_exit((void*)result);
}
```

## Creating Array of Threads

- You may need to create large number of threads for dividing computational tasks as per your program logic
- At compile time, if yoou know number of threads you need, yoou can simply create an array of type `pthread_t` too store thread IDs
- If you doo not know at compile time the number of threads yoou need youo may have to allocate memory on heap for storing thread IDs
- Max number of threads that a system allows can be seen in `/proc/sys/kernel/threads-max`
    * There are other parameters that limit this couont e.g., size of stack the system needs to give too every new thread
- Example:
```
#include <sys/types.h>
#include <linux/unistd.h>
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void * f1(void * arg);
int main(int argc, char* argv[]){
   char* msg[] = {"Thread1", "Thread2", "Thread3", "Thread4", "Thread5"};
   pthread_t tids[5];
   for(int i=0; i<5; i++)
      pthread_create(&tids[i], NULL, f1, (void*)msg[i]);
   for(int i=0; i<5; i++)
      pthread_join(tids[i], NULL);
   printf("main(): Reporting that all child threads have terminated\n");
   exit(0);
}

void * f1(void * arg){
   printf("I am child %s\n", (char*)arg);
   pthread_exit(NULL);
}
```
- Example:
```
#include <sys/types.h>
#include <linux/unistd.h>
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int thread_no = 0;

void * f1(void * arg);
int main(int argc, char* argv[]){
   if(argc != 2){
      printf("Invalid arguments, must pass one integer value...\n");
      exit(1);
   }
   int ctr = atoi(argv[1]);
   // Stored on heap
   pthread_t* tid =  (pthread_t*)malloc(sizeof(pthread_t)*ctr);
   for(int i=0;i<ctr;i++)
      pthread_create(&tid[i], NULL, f1, NULL);
   for(int j=0;j<ctr;j++)
      pthread_join(tid[j], NULL);
   printf("main(): Reporting that all child threads have terminated\n");
   exit(0);
}

void * f1(void * arg){
   int thread_id = thread_no; thread_no++;
   fprintf(stderr, "I am child thread number %d \n", thread_id);
   pthread_exit(NULL);
}
```
- Example:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>  //exit
#include <math.h>
#include <unistd.h>

void * f1(void *);
int *arr1;
int *arr2;
int *result;
int main(int argc, char* argv[]){
   if(argc != 2){
      printf("Invalid arguments, must pass one integer value...\n");
      exit(1);
   }
   int size = atoi(argv[1]);
   //allocate memory for three integer arrays on heap
   arr1   = (int*)malloc(sizeof(int)*size);
   arr2   = (int*)malloc(sizeof(int)*size);
   result = (int*)malloc(sizeof(int)*size);
   //get input from user
   printf("\nEnter  %d values for array1\n",size);
   for(int i=0; i<size; i++)
      scanf("%d",&arr1[i]);
   printf("\nEnter  %d values for array2\n", size);
   for(int i=0; i<size; i++)
      scanf("%d",&arr2[i]);

//allocate memory for size number of thread IDs on heap
   pthread_t* tid =  (pthread_t*)malloc(sizeof(pthread_t)*size);
//create the threads and join them
//limitation of executing following two functions inn one single loop is that all threads will execute one after another and not concurrently
   for(int i=0; i<size; i++){
      pthread_create(&tid[i], NULL, f1, (void*)&i);
      pthread_join(tid[i], NULL);
	}
   printf("\nI am main thread.Sum of the two arrays is: \n");
   for(int j=0; j<size; j++)
	   printf("%d\n",result[j]);
   return 0;
}

void * f1(void * args){
   int n = *((int*)args);
   result[n] = arr1[n] + arr2[n];
   pthread_exit(NULL);
}
```

## Point to Ponder

- `errno` is a global per-prcess variable used to store the error number occurred in the alst failed system call
- What problem can occur due to this shared variable in a multi-threaded proogram
    * Problem is that two oor more threads can encounter errors, all causing same `errno`
    * A thread might end up  checking `errno` after it has already been updated by another thread
    * Solution is too make `errno` local t oevery thread so setting it in one thread does not affect its value in any oother thread
        + Compiling with `-D_REENTRANT` flag to `gcc`

## Another point to ponder

- All threads have same PID as returned by `getpid()` system call
- How to uniquely identify a thread within a multi-threaded process
    * Use `gettid()` and `pthread_self()`
    * `gettid()` TID:
        + Assigned by kernel, similar to PIDs
        + May be reused after a very long time once PID couonter reaches max value
        + Unique accross system
    * `pthread_self()` TID:
        + POSIX TIDs maintained by thread implementation
        + Reused after completion of thread
        + Unique within process only
    * Since `gettid()` is Linux specific, it is not portable
- Example:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

void * f1(void *);
int main(){
   pthread_t tid1, tid2;
   printf("PID using getpid() in main: %ld\n",(long)getpid());
   printf("Main TID using gettid():%ld\n",(long)syscall(SYS_gettid));
   pthread_create(&tid1, NULL, f1, NULL);
   pthread_create(&tid2, NULL, f1, NULL);
   while(1);
   return 0;
}
void* f1(void* arg){
   printf("PID using getpid() in f1(): %ld\n",(long)getpid());
   printf("Child TID using gettid():%ld\n",(long)syscall(SYS_gettid));
   while(1);
   pthread_exit(NULL);
}
```
- `/proc/<process ID>` has subdirectories:
    * `/proc/<process ID>/<thread ID 1>`
    * `/proc/<process ID>/<thread ID2>`
    * ...
- Note: the main thread has same TID as PID and its child threads are increments of it
- Example:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

void * f1(void *);
int main(){
   char* msg[] = {"Thread1", "Thread2", "Thread3"};
   pthread_t tids[3];
   for(int i=0; i<3; i++)
      pthread_create(&tids[i], NULL, f1, (void*)msg[i]);
   for(int i=0; i<3; i++)
      pthread_join(tids[i], NULL);
   return 0;
}

void* f1(void* arg){
   printf("PID of %s using getpid(): %ld\n",(char*)arg, (long)getpid());
   printf("TID of %s using gettid():%ld\n",(char*)arg, (long)syscall(SYS_gettid));
   printf("TID of %s using pthread_self():%ld\n\n",(char*)arg, (long)pthread_self());
//	while(1);
   pthread_exit(NULL);
}
```

## Thread attributes

- Every thread has a set of attributes which can be set befoore creating it
    * If we pass NULL as second arguement to `pthread_create()` the default thread attributes are used
    * Default values of thread attributes shoown below:
        1. `detachedstate`: (`PTHREAD_CREATE_JOINABLE`) joinable by oother threads
        2. `stackaddr`: (NULL) stack allocated by system
        3. `stacksize`: (NULL)2MB
        4. `priority`: (---) priority of calling thread is used
        5. `policy`: (`SCHED_OTHER`) determined by system
        6. `inheritsched`: (`PTHREAD_INHERIT_SCHED`) inherit scheduling attributes from creating thread

## Detach state

- Joinable thread
    * Not automatically cleaned up by Linux when it terminates
    * Thread's exit status hands until another thread calls `pthread_join()` to obtain its return value
    * Only then is its resources released
- Detached thread
    * Detachable thread is cleaned up automaticaly when it terminates
    * Anoother thread may not wait for its completion using `pthread_join()` to obtain its return value
    * A thread can detach itself with `pthread_detach(pthread_self())` call
- Example:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void* f1(void *);
int thread_finished = 0;
int main(){
   pthread_t tid;
//create a pthread attribute object
   pthread_attr_t thread_attr;
//Initialize the pthread attribute object
   pthread_attr_init(&thread_attr);
//Modify the attribute object to contain the desired attribute(s)
   pthread_attr_setdetachstate(&thread_attr, PTHREAD_CREATE_DETACHED);
//Create thread with modified attributes
   pthread_create(&tid, &thread_attr, f1, NULL);
//Destroy pthread attribute object
   pthread_attr_destroy(&thread_attr);
   while(thread_finished == 0){
      printf("Waiting for child thread to finish...\n");
      sleep(2);
   }
   printf("Main thread exiting,Bye!\n");
   return 0;
}

void * f1(void* args){
   printf("Child thread is running...\n");
   sleep(8);
   printf("Child thread setting the finished flag, and exiting.\n");
   thread_finished = 1;
   pthread_exit(NULL);
}
```

## Another point to ponder

- If a singal is sent too a multi-threaded process, which thread will receive the signal
- Unix signal model was designed with Unix process model in mind so othere are conflicts between signal and thread models
- Combining singals and threads is complex and should be avoided when possible
- Keep in mind:
    * Signal handlers are per-process
    * Signal masks are per-thread
    * Sending a signal using `kill(1)` or `kill(2)` will terminate the process
    * You can use `pthread_kill(3)` to send a signal to another thread in the same process
    * If one thread ignores a signal, then that signal is ignored by all threads
- What happens if one o the threads call `exec()` system call
    * When any thread calls one of the `exec()` functions, the calling program is completely replaced and all threads except the one that called `exec()` vanishes immediately
    * None of the threads executes destructors for thread-specific data or calls cleanup handlers
    * All pthread objects (mutexes and condition variables) disappear as the new program overwrites the memory of the rpoocess
    * After an `exec()` thread ID of the remaining thread is unspecified
- If one thread executes `fork()` does new process duplicate onliy calling thread or all threads?
    * Is child process single threaded or multi-threaded?
    * Child process is created with a single thread - the one that called `fork()`
    * Recommended that `fork()` in a multi-threaded process should always be followed immediately by `exec()` so that all global variables as well as pthread objects disappear as the child program overwrites memory of the process
    * If there is no `exec()` after the `fork()` then the state of global variables as well as all pthread objects are preserved in the child which may cause problems in child program
    * So for programs that use `fork()` but noot `exec()` afteewards, pthread API provides a way to define fork handlers using `pthread_atfork()`
        + These handlers are preserved after `fork()` but not after `exec()`
- What if main thread wants to cancel another thread or threads
    * Thread can call `pthread_cancel()` to request that another thread by cancelled by mentioning the TID of the target thread
    * Cancellatioon may cause problem if target thread is holding some resources which it frees later
    * Possible for a thread to make itself cancellable by calling a function `pthread_setcancelstate()`
    * Cancellable thread can also set its cancel type vby calling `pthread_setcanceltype()` which can be asynchronous (thread can be cancelled at any time in its execution) or deferred (cancellation request is queued until target thread reaches next cancellation point)