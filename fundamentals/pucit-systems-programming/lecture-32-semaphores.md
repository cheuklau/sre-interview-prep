# Lecture 32

## Introduction to Semaphores

- Semaphores are a kind of generalized locks first defined in the 60s
- Primiteive used to provide synchronization ebtween processes or between various threads of a process
- Considered as an integer bariable with three differences:
    1. When you create a semaphore, you can initilzie it to any integer value but after you can perform two operations:
        * Increment (verhogen, post, signal)
        * decrement (proberen, wait)
    2. When a process/thread decrements the semaphore, if semaphore currently has the value zero then the thread blocks until the value of semaphore value rises above zero
    3. When a process/thread increments the semaphore, if there are other threads waiting, one of the waiting threads gets unblocked

## Comparison between mutex, condition variable and semaphore

- Mutex can have only two values 0 or 1 and is used to achieve mutual exclusion
    * Semaphores can also be used as counting semaphores in order to access a shared pool of resources
- Mutex must always be unlocked by the thread that locked the mutex
    * Semaphore post need not be performed by same thread that did the semaphore wait
- When condition variable is signaled, if no thread is waiting for this condition variable, the signal is lost
    * Semaphore post is always rememebred
- Out of various synchronization tehcnqiues, only function that can be called from a singla handler is semaphore post
- Mutexes are optimized for locking, condition variables are optimized for waiting and semaphore can do both

## Implemntations of POSIX semaphores

1. Named semaphores
    * `sem_open()`
2. Unnamed/memory based semaphores
    * `sem_init()`
- Both go to
    * `sem_wait()`
    * `sem_trywait()`
    * `sem_post()`
    * `sem_getvalue()`
- Then:
    * For named: `sem_close()` and `sem_unlink()`
    * For unnamed: `sem_destroy()`

## Creating a Named Semaphore

- Assume we created `/dev/shm/sem.name1`
- Processes can simply open and use `sem.name1`
- `sem_open()` library call creates a new semaphore or opens an existing one by identifying its `name`
- return value is `sem_t` datatype which is used as arugment to `sem_wait()`, `sem_post` and `sem_close()`
- `sem_wait()` library call decremennts the semaphore pointed to by `sem`
- `sem_post()` library call implements the semaphore pointed to by `sem`; if semaphore value > 0 then another process or thread blocked in a `sem_wait()` call will be woken up and proceed
- `sem_trywait()` is same as `sem_wait()` except if decrement cannot be immediately performed it returns an error instead of blocking
- `sem_getvalue()` to get the value of a semaphore
- `sem_close()` closes a named semaphore
- Closing a semaphore does not remove it from the system as they are kernel persistent
    * Retains value even if no process currently has semaphore open
- To remove named semaphore from system need to use `sem_unlink()` call
    * Can also use `rm` to deleted the related file in `/dev/shm/`

## Example

- Example showing race condition:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <semaphore.h>
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
   for(long i=0;i<10000000;i++){
		balance++;
   }
   pthread_exit(NULL);
}
void * dec(void * arg){
   for(long j=0;j<10000000;j++){
		balance--;
    }
   pthread_exit(NULL);
}
```
- Solution of above with semaphores:
```
#include <pthread.h>
#include <fcntl.h>           /* For O_* constants */
#include <sys/stat.h>        /* For mode constants */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <semaphore.h>
long balance = 0;//global variable
void * inc(void * arg);
void * dec(void * arg);
sem_t *mutex;
int main(){
   char* name = "/sem1";
	mutex = sem_open(name, O_CREAT, 0666, 1);
   pthread_t t1, t2;
   pthread_create(&t1, NULL, inc,NULL);
   pthread_create(&t2, NULL, dec,NULL);
   pthread_join(t1, NULL);
   pthread_join(t2, NULL);
	sem_close(mutex);
   sem_unlink(name);
   printf("Value of balance is :%ld\n", balance);
   return 0;
}
void * inc(void * arg){
   for(long i=0;i<10000000;i++){
      sem_wait(mutex);
		balance++;
		sem_post(mutex);
   }
   pthread_exit(NULL);
}
void * dec(void * arg){
   for(long j=0;j<10000000;j++){
      sem_wait(mutex);
		balance--;
		sem_post(mutex);
    }
   pthread_exit(NULL);
}
```
- Example showing race condition with shared memory:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <semaphore.h>
#include <sys/ipc.h>
#include <sys/shm.h>

void inc();
void dec();
long *balance;
int main(){
//balance variable should be located in shared memory
   key_t key1 = ftok("file1", 65);
   int shm_id1=shmget(key1, 8, IPC_CREAT | 0666);
   balance = (long*)shmat(shm_id1, NULL, 0);
   *balance=0;   //initializing balance

int cpid = fork();
   if (cpid == 0){
       inc();
       shmdt(balance);
       exit(0);
   }
   else{
       dec();
       waitpid(cpid,NULL,0);
       printf("Value of balance is: %ld\n", *balance);
       shmdt(balance);
       shmctl(shm_id1, IPC_RMID, NULL);
       return 0;
   }
}
void inc(){
   for(long i=0;i<100000000;i++){
		*balance = *balance + 1;
   }
}
void dec(){
   for(long j=0;j<100000000;j++){
		*balance = *balance - 1;
    }
}
```
- Example of above solved with semaphores:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <semaphore.h>
long balance = 0;//global variable
void * inc(void * arg);
void * dec(void * arg);
sem_t *mutex;
int main(){
   char* name = "/sem1";
	mutex = sem_open(name, O_CREAT, 0666, 1);
   pthread_t t1, t2;
   pthread_create(&t1, NULL, inc,NULL);
   pthread_create(&t2, NULL, dec,NULL);
   pthread_join(t1, NULL);
   pthread_join(t2, NULL);
	sem_close(mutex);
   sem_unlink(name);
   printf("Value of balance is :%ld\n", balance);
   return 0;
}
void * inc(void * arg){
   for(long i=0;i<10000000;i++){
      sem_wait(mutex);
		balance++;
		sem_post(mutex);
   }
   pthread_exit(NULL);
}
void * dec(void * arg){
   for(long j=0;j<10000000;j++){
      sem_wait(mutex);
		balance--;
		sem_post(mutex);
    }
   pthread_exit(NULL);
}
```
- Example:
```
#include <pthread.h>
#include <semaphore.h>
#include <stdio.h>

void * f1(void *);
void * f2(void *);
void * f3(void *);
int main() {
   pthread_t t1, t2,t3;
   pthread_create(&t1, NULL, f1, NULL);
   pthread_create(&t2, NULL, f2, NULL);
   pthread_create(&t3, NULL, f3, NULL);
   pthread_join(t1, NULL);
   pthread_join(t2, NULL);
   pthread_join(t3, NULL);
   printf("\n");
   return 0;
}
void * f1(void * parm){
   printf(" Arif Butt");
}
void * f2(void * parm){
   printf(" fun with");
}
void * f3(void * parm){
   printf(" Learning is");
}
```
- Example solving above by serializing with semaphore:
```
#include <pthread.h>
#include <fcntl.h>           /* For O_* constants */
#include <sys/stat.h>        /* For mode constants */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <semaphore.h>

void * f1(void *);
void * f2(void *);
void * f3(void *);
sem_t *semA, *semB;
int main() {
   char* name1 = "/sem1";
   char* name2 = "/sem2";
	semA = sem_open(name1, O_CREAT, 0666, 0);
   semB = sem_open(name2, O_CREAT, 0666, 0);
   pthread_t t1, t2,t3;
   pthread_create(&t1, NULL, f1, NULL);
   pthread_create(&t2, NULL, f2, NULL);
   pthread_create(&t3, NULL, f3, NULL);
   pthread_join(t1, NULL);
   pthread_join(t2, NULL);
   pthread_join(t3, NULL);
while(1);
   sem_close(semA);
   sem_close(semB);
   sem_unlink(name1);
   sem_unlink(name2);
   printf("\n");
  return 0;
}
void * f1(void * parm){
   sem_wait(semB);
   fprintf(stderr, " Arif Butt");
}
void * f2(void * parm){
   sem_wait(semA);
   fprintf(stderr, " fun with");
   sem_post(semB);
}
void * f3(void * parm){
   fprintf(stderr," Learning is");
   sem_post(semA);
}
```

## Creating an unnamed semaphore

- Memory based semaphore shared between two threads
- Memory based semaphore must be placed in a shared memory between two processes
- `sem_init()` library call initilzis the unnamed semaphore at the address space pointed to by first argumetn `sem` with value mentioned in third argument
    * If `pshared` is zero then semaphore is shared between threads of a process
    * If `pshared` is non-zero then semaphore is shared between processes and `sem` has to be located in a region of shared memory
- `sem_destroy()` destroys the unnamed semaphore

## Example

- Example of previous solution using unnamed semaphores:
```
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <semaphore.h>
long balance = 0;//global variable
void * inc(void * arg);
void * dec(void * arg);
sem_t mutex;
int main(){
   sem_init(&mutex, 0, 1); //initializing semaphore
   pthread_t t1, t2;
   pthread_create(&t1, NULL, inc,NULL);
   pthread_create(&t2, NULL, dec,NULL);
   pthread_join(t1,NULL);
   pthread_join(t2,NULL);
	sem_destroy(&mutex);
   printf("Value of balance is :%ld\n", balance);
   return 0;
}
void * inc(void * arg){
   for(long i=0;i<10000000;i++){
      sem_wait(&mutex);
		balance++;
		sem_post(&mutex);
   }
   pthread_exit(NULL);
}
void * dec(void * arg){
   for(long j=0;j<10000000;j++){
      sem_wait(&mutex);
		balance--;
		sem_post(&mutex);
    }
   pthread_exit(NULL);
}
```