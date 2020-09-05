# Lecture 18

## Process creation using vfork()

- In bad old days a `fork()` require making complete copy of parent data space
    * Overhead because immediately after the child calls `exec()`
    * For better efficiency, `vfork()` was introduced
- `vfork()` creates a new process when purpose of new process is to `exec` a new proogram
- features that make `vfork()` more efficient than `fork()` are:
    1. No duplicatioon of virt memory pages in child process
        * Child shares parent's address space until it either performs `exec()` or call `exit()`
    2. Executioon of parent process suspended until child has performed an `exec()` or `exit()`
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
int main(){
   pid_t cpid = vfork();
   if (cpid == 0){
      sleep(1);
      printf("Hello I am child..\n");
      sleep(2);
      printf("Hello I am child again, I am exitting.\n");
      sleep(2);
      exit(0);
   }
   else{
      printf("\nHello I am parent, my child has terminated\n");
      exit(0);
   }
}
```
- Note: that parent suspends until child exits in above code
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int gvar = 54;
int main(){
   int lvar = 100;
   printf("Before fork()\n");
   pid_t cpid = vfork();
   if (cpid == 0){
      gvar++;
      lvar++;
      printf("I am child and I have incremented my gvar and lvar\n");
      printf("Global var= %d, Local var= %d\n",gvar,lvar);
      exit(0);
   }
   else{
      printf("\nI am parent now...\n");
      printf("Global var= %d, Local var= %d\n",gvar,lvar);
      exit(0);
   }
}
```
- Above shows that child operates in parent's address space by accessing its parents local variables
- Example to shoow `vfork()` more efficient that `fork()`:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(){
   for(int i = 0; i < 100; i++){
      fork();
//      vfork();
   }
   exit(0);
   }
```
- Above shows `fork()` takes much more time to complete

## Copy-on-write semantics

- Today most OSs implement `fork()` using copy-on-write pages so othe only penalty incurred by `fork()` is the time and memory required
    1. To duplicate the parent's page table
    2. To ocreate a unique task structure for the child
- Parent forks a child process
    * Child gets a copy of parent's page table
    * Pages which may change are marked copy-on-write i.e., the pages are not copied for the child rather the child starts sharing pages and writable pages are marked copy-on-write
- What happens when child reads the page?
    * Just access same memory as parent
- What happens when child/parent writes the page
    * If either process (child/parent) tries to modify a shared page, a page fault occurs and the page is copied and iserted in the page table for that particular process
    * The other process (who later faults oon write) discovers it is the only owner so ono copying takes place

## Orphan processes

- If parent terminated befoore reaping children, and chld process still running then these children are orphans
    * They are adopted by `init` which does the reaping
        + New systems have systemd performing the reaping
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(){
   pid_t cpid = fork();
   if (cpid == 0){
      printf("Running child, PID=%ld PPID=%ld\n",(long)getpid(), (long)getppid());
      while(1);
   }
   else{
      printf("Terminating parent, PID=%ld PPID=%ld\n",(long)getpid(), (long)getppid());
      exit(0);
   }
   return 0;
}
```

## Zombie processes

- Processes which have terminated but their parent have not coollected their `exit` status and has not reaed them are called zoombies or defunct
    * So a parent must reap its children
- When process terminates but is still holding system resources e.g., PCB and various tables maintained by OS, it is half-alive and half-dead because it is still holding resources like memory but it is never scheduled on the CPU
- Zombies can't be killed by a signal (even `SIGKILL`)
    * OOnly way to remove them from the system is to kill their parent
    * At which time they become an orphan and adopted by `init` or `systemd`
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
int main(){
   pid_t cpid = fork();
   if (cpid == 0){
      printf("Terminating child with PID = %ld\n", (long)getpid());
      exit (0);
   }
   else{
      printf("Running parent, PID=%ld\n",(long)getpid());
      while(1);
      }
   return 0;
}
```
- Above program creates a zombine marked as `defunct` in `ps`

## Monitoring Child Process

- Parent process monitor child processes using `wait` family of system calls
- `wait()` system call
    * `pid_t wait(int *status)`
    * Process that calls `wait()` system call gets blocked until any oone of its child terminates
    * The child process returns its termination status using the `exit()` call and that integer value is received by the parent inside the `statuus` argument
        + This is used for reaping and cleaning zombies from system
    * On shell, we check this value using `$?` env var
    * On success, `wait()` sys call returns PID of the terminated child and in case of error returns a `-1`
    * If process wants to wait for termination of all its children then use `while(wait(null) > 0);`
- Two purposes of `wait()` system call:
    1. Notify parent that a child process finished running
    2. Tell parent how a child process finished
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
int main(){
   pid_t cpid = fork();
   if (cpid == 0){
      printf("Hello I m Child.\n");
      sleep(1);
      printf("I m Child again, and my PID is %ld\n", getpid());
      sleep(1);
      printf("I m Child again, and I am terminating...\n");
      sleep(1);
      exit(7);
   }
  else{
   int status;
   // Wait for child to finish and return code
   pid_t rv = wait (&status);
   printf ("Hello I m Parent.\n");
   printf("Return value of wait is %ld, and status is %d\n",rv,status);
   exit(54);
   }
}
```

## wait() status argument

- A process can end in fouor ways:
    1. Success/failure
        * On success program calls `exit(0)` or `return 0` from `main()`
        * On failure program calls `exit()` with non-zero value
    2. Killed by a signal
        * Process might get killed by a signal from keyboaord, from interval timer, from kernel or another process
    3. Stopped by a signal
        * `SIGSTOP` and temporary suspend execution
    4. Continued by a signal
        * `SIGCONT` and continue execution
- `wait()` status argument
    * All this info is encoded in the `status` argument of `wait()` system call
    * Programmer can decipher this using bit operators or available macros
    * Normal termination
        + Upper 8 bits contain exit status (0-255), lower 8 bits 0
    * Killed by signal
        + Upper 8 bits contains 0, lower 8 bits contain termination signal
    * Stopped by signal
        + Upper 8 bits contain stop signal, lower 8 bits contain 0x7f
    * Continued by a signal
        + 0xFFFF covers all 16 bits
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
int main(){
   pid_t cpid = fork();
   if (cpid == 0){
      printf("Hello I m Child.\n");
      sleep(1);
      printf("I m Child again, and my PID is %ld\n", getpid());
      sleep(1);
      printf("I m Child again, and I am terminating...\n");
      sleep(1);
      exit(7);
   }
  else{
   int status;
   pid_t rv = wait (&status);
   printf ("Hello I m Parent.\n");
   int low_8 = status & 0xff;
   // Shift status by 8 bits to the right
   int high_8 = status >> 8;
   // Process terminated noormally
   if(low_8 == 0)
   	printf("Return value of wait is %ld, and status is %d\n",rv, high_8);
   exit(54);
   }
}
```
- Now output shows exit code of 7
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
void disp_status(int);
int main(){
   pid_t cpid = fork();
   if (cpid == 0){
      printf("I am child process and I am running...\n");
      //exit(7);
      int j = 0;
      int i = (2 / j);
 }
  else{
   int status;
   pid_t rv = wait (&status);
   printf ("Hello I m Parent.\n");
   disp_status(status);
   exit(54);
   }
}


void disp_status(int status){
//normal termination
   int low_7 = status & 0x7f;
   int high_8 = status >> 8;
   if(low_7 == 0)
      printf("My child terminated normally with exit value %d\n", high_8);
//killed by a signal
   if(high_8 == 0)
      printf("My child was killed by Signal Number = %d\n", low_7);
   int bit_7 = status & 0x80;
   bit_7 = bit_7 >> 7;
   if(bit_7 == 1)
      printf("Core Dump file generated.\n");
//stopped by a signal
   if(low_7 == 0x7F)
      printf("My child was stopped by Signal Number = %d\n", high_8);
//continued by SIGCONT
   int low_16 = status & 0xffff;
   if(low_16 == 0xffff)
      printf("My child continued its execution due to SIGCONT\n");
}
```

## Macros for wait() status arguments

- Instead of bit operators, we can use macros to decipher `status` argument of `wait()` defined in `/usr/include/x86_64-linux-gnu/bits/waitstatus.h`
    * `WIFEXITED`: true if child process exited noormally
    * `WIFSIGNALED`: returns true if child process killed by signal
    * `WIFSTOPPED`: returns true if child process stopped by a signal
    * `WIFCONTINUED`: returns true if child process resumed by `SIGCONT`
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
void disp_status(int);
int main(){
   pid_t cpid = fork();
   if (cpid == 0){
      printf("I am child process and I am running...\n");
//      exit(7);
      int j = 0;
      int i = (2 / j);
 }
  else{
   int status;
   pid_t rv = wait (&status);
   printf ("Hello I m Parent.\n");
   disp_status(status);
   exit(54);
   }
}


void disp_status(int status){
//normal termination
if(WIFEXITED(status))
      printf("My child terminated normally with exit value %d\n", WEXITSTATUS(status));
//killed by a signal
  else if (WIFSIGNALED(status)){
     printf("My child was killed by Signal Number = %d\n",WTERMSIG(status));
     if(WCOREDUMP(status))
        printf("Core Dump file generated.\n");
}
//stopped by a signal
  else if (WIFSTOPPED(status))
     printf("My child was stopped by Signal Number = %d\n", WSTOPSIG(status));
//continued by SIGCONT
  else if (WIFCONTINUED(status))
printf("My child continued its execution due to SIGCONT\n");
}
```
- Above is same as before but using macros

## Limittations of wait() system call

- Using `wait()` it is not possible for parent to retrieve the signal number using execution which the execution of a child process is stopped
    * It is also not possible to be notified when a stopped child is resumed by delivery of a signal
- It is not poossible to wait for a particular child, parent can only wait for the first child that terminates
- It is not possible to perform a non-blocking wait so that if no child has yet terminated, parent gets an indication of this fact
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
void disp_status(int);
int main(){
   pid_t cpid = fork();
   if (cpid == 0){
     printf("I am child and my PID is %ld\n", getpid());
      //exit(7);
     while(1);
 }
  else{
   int status;
   pid_t rv = wait (&status);
   printf ("Hello I m Parent.\n");
   disp_status(status);
   exit(54);
   }
}


void disp_status(int status){
//normal termination
   int low_7 = status & 0x7f;
   int high_8 = status >> 8;
   if(low_7 == 0)
      printf("My child terminated normally with exit value %d\n", high_8);
//killed by a signal
   if(high_8 == 0)
      printf("My child was killed by Signal Number = %d\n", low_7);
   int bit_7 = status & 0x80;
   bit_7 = bit_7 >> 7;
   if(bit_7 == 1)
      printf("Core Dump file generated.\n");
//stopped by a signal
   if(low_7 == 0x7F)
      printf("My child was stopped by Signal Number = %d\n", high_8);
//continued by SIGCONT
   int low_16 = status & 0xffff;
   if(low_16 == 0xffff)
      printf("My child continued its execution due to SIGCONT\n");
}
```

## waitpid() system call

- UNIX designers have added a number of variants of `wait()`
    * `waitpid()`, `waitid()`, `wait3()`, ...
- `pid_t waitpid(pid_t pid, int* status, int options)`
    * `pid` enables selection of child to be waited for
    * If `pid>0` waits for child whose PID equals `pid`
    * If `pid==-1` waits for any child
    * If `pid=0` waits for any child process whose process Group ID is the same as the calling parent process
    * If `pid<-1` waits for any child process whose process Group ID equals the absolute value of `pid` argument
    * Third argument of `waitpid()` call is a bit mask of zero or more of the following flags:
        1. `WUNTRACED` returns info when a child is stopped by a signal
        2. `WCONTINUED` return info about stopped children that ahve been resumed by `SIGCONT`
        3. `WNOHANG` performs polling; if no child specified by pid has yet changed state then return immediately instead of blocking
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
void disp_status(int);
int main(){
   pid_t cpid = fork();
   if (cpid == 0){
      printf("I am child and my PID is %ld\n", getpid());
   while(1);
 }
  else{
   int status;
   pid_t rv = waitpid(cpid, &status, WUNTRACED | WCONTINUED);
   printf ("Hello I m Parent.\n");
   disp_status(status);
   exit(54);
   }
}


void disp_status(int status){
//normal termination
   int low_7 = status & 0x7f;
   int high_8 = status >> 8;
   if(low_7 == 0)
      printf("My child terminated normally with exit value %d\n", high_8);
//killed by a signal
   if(high_8 == 0)
      printf("My child was killed by Signal Number = %d\n", low_7);
   int bit_7 = status & 0x80;
   bit_7 = bit_7 >> 7;
   if(bit_7 == 1)
      printf("Core Dump file generated.");
//stopped by a signal
   if(low_7 == 0x7F)
      printf("My child was stopped by Signal Number = %d\n", high_8);
//continued by SIGCONT
   int low_16 = status & 0xffff;
   if(low_16 == 0xffff)
      printf("My child continued its execution due to SIGCONT\n");
}
```