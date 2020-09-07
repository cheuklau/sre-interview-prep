# Lecture 25

## Sending Signals to Processes in C Program

## kill() system call

- `int kill(pid_t pid, int sig);`
- One process can send a signal to another process using `kill()` system call
- `pid` identifies one or more processes to which signal specified by `sig` is to be sent
- if `sig` is zero then normal error checking is performed but no signal is sent
    * Used to determine if a specified process still exists
- if no process matches specified `pid` then `kill()` fails and sets `errno` to `ESRCH`
- four different cases determine how `pid` is interpreted:
    * if `pid>0` then signal is sent to process with pid
    * if `pid==0` then signal is sent to every process in the same process group as the calling process including the process itself
    * if `pid<-1` signal is sent to every process in the process group whose `PGID` equals the absolute value of `pid`
    * if `pid==-1` signal is sent to every process for which calling process has permission to send a signal except `init` and the calling rpocess
        * If a privileged process makes this call then all processes on system will be signaled except for those last two

## raise() library call

- `int raise(int sig);`
- sometimes useful for process to send a signal to itself
    * `raise()` function performs this task
- in a single-threaded program a call to `raise()` is equivalent to the following call to `kill()`
    * `kill(getpid(), sig)`
- when process sends itself a signal using `raise()` or `kill()` the signal is delivered immediately i.e., before `raise()` returns to the caller
- note that `raise()` returns a nonzero value (not necessarily `-1`) on error
    * the only error that can occur with `raise()` is `EINVAL` because `sig` was invalid

## abort() library call

- `abort()` function terminates the calling process by raising a `SIGABRT` signal
    * Defatul action for `SIGABRT` is to produce a core dump file and terminate the process
    * Core dump file can then be used within a debugger to examine state of the program at the time of the `abort()` call
- `abort()` function never returns

## pause() system call

- `pause()` system call causes the invoking process/thread to sleep until a signal is received that either terminates it or causes it to call a signal catching function
- `pause()` function only returns when a signal was caught and the signal-catching function returned
    * in this case `pause()` returns `-1` and `errno` is set to `EINTR`

## alarm() system call

- `unsigned int alarm(unsigned int seconds);`
- `alarm()` system call is used to ask OS to send calling process a special signal `SIGALARM` after a given number of seconds
    * If seconds is zero no new alarm is created
- function returns the previouslyly registered alarm clock for the process that has not yet expired i.e., the number of seconds left for that alarm clock is returned as the valu of this function
- unix systems do not operate as real-time systems so process might receive this signal after a longer time than requested
    * only one alarm clock per process
    * uses: check timeouts, check some condition on a regular basis e.g., server response after 30 seconds; if not notify user and exit

## Adding a delay: using sleep()

- `int sleep(unsigned int secs);
- causes the callilng thread to sleep (suspend execution) either until number of specified seconds have elapsed or until a signal arrives which is not ignored
- returns zero if requested time has elapsed or the number of seconds left to sleep, if the call was interrupted by a signal handler

## Examples

- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(){
   printf("I am a running process!\n");
   sleep(1);
   printf("I am going to divide a number with zero!\n");
   sleep(1);
   int a=3, b=3;
   float ans = 54/(a-b);
   return 0;
}
```
- Running above generates a floating point exception `SIGFPE`
- `ulimit -c unlimited` to set core file size to unlimited (default was zero)
- Run it again and we see a core file; make sure to set it back to zero or you will hit storage issues
- Example:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(){
 while(1) {
   printf("I am in an infinite loop! Press <CTRL+C> to exit\n");
   sleep(1);
 }
 return 0;
}
```
- Above prints a statement every second
- Hit `ctrl-c` to send process to background, `fg %1` to send it back to foreground
- `man kill` and `man 2 kill` to see built-in and system call
- Example:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(){
   printf("After five seconds, I will get a SIGHUP signal\n");
   sleep(5);
   kill(getpid(),1);
//   raise(1);
   printf("This will not be printed");
   return 0;
}
```
- Above program raises a `SIGHUP` to itself then exits
- Example:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(){
   pid_t cpid = fork();
   if (cpid ==0){
      for(;;){
         printf("I am child in an infinite loop\n");
         sleep(1);
      }
   }
   else{
      sleep(5);
      kill(cpid,SIGSEGV);
      printf("I have killed my child... Bye\n");
      exit(0);
   }
}
```
- Above progarm creates a fork of a child process in an infinite loop
- Parent then sends `SIGSEGV` to child process which terminates it then the parent process exits
- Example:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(){
   int i = alarm(205);
   printf("i contains: %d\n", i); // 0 since no alarm was created before
   sleep(5);
   int j = alarm(10);
   printf("After alarm(10); j contains: %d\n", j); // 200 since 5 seconds have passed since first alarm
   sleep(100);
   exit(0);
}
```

## signal() system call

- `sighandler_t signal(int signum, void (*sh)(int));`
- To change the disposition of a particular signal a programmer can use the `signal()` system call which installs a new signal handler for the signal with number `signum`
- Second parameter can have three values
    1. `SIG_IGN`: signal is ignored
    2. `SIG_DFL`: default action associated with signal occurs
    3. User specified function addresse which is passed an integer argument and returns nothing
- `signal()` system call returns the previous handler or `SIG_ERR` on error
- Signals `SIGKILL` and `SIGSTOP` cannot be caught
    * Behavior of a process is undefined after it ignores `SIGFPE`, `SIGILL` or `SIGSEGV` signal that was not generated by `kill()` or `raise()` functions
- Example:
```
void (*old handler)(int);
old handler = signal(SIGINT, newhandler);
...
... // if SIGNINT is delivered, new handler will be used to handle signal
...
if (signal(SIGINT, oldhandler) == SIG_ERR) { ... }
...
... // if SIGINT is delivered, oldhandler will be used to handle signal
...
```

## Examples

- Example for ignoring signal
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(){
 signal(SIGINT,SIG_IGN);
 signal(SIGFPE, SIG_IGN);
 while(1) {
   printf("I am in an infinite loop!\n");
   printf("You can't kill me by SIGINT <2> or SIGFPE <8>\n");
   sleep(2);
 }
 return 0;
}
```
- Above program sets `SIGINT` and `SIGFPE` to be ignored via `SIG_IGN`
- Example for writing our own signal handler:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
void  myhandler(int signum){
   printf("\nHey, I got a signal: %d\n\n",signum);
}

int main(){
   signal( SIGINT, &myhandler ); // now when we send process SIGINT it goes to myhandler function
   while(1) {
	printf("I am in an infinite loop!\n");
	sleep(1);
   }
   return 0;
}
```
- Example of writing multiple signal handlers
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
void sigint_handler(int signum){
  printf("\nHey, I got SIGINT: %d\n\n",signum);
  signal(SIGINT,SIG_DFL); // sets back to default setting (2 in this case)
}
void sigquit_handler(int signum){
  printf("\nHey, I got SIGQUIT: %d\n\n",signum);
  signal(SIGQUIT,SIG_DFL);
}
void sigtstp_handler(int signum){
  printf("\nHey, I got SIGTSTP: %d\n\n",signum);
  signal(SIGTSTP,SIG_DFL);
}

int main(){
   signal(SIGINT,sigint_handler);
   signal(SIGQUIT, sigquit_handler);
   signal(SIGTSTP, sigtstp_handler);
   while(1) {
	printf("I am in an infinite loop!\n");
	sleep(1);
   }
   return 0;
}
```
- Example of a single handler handling multiple signal types:>
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
void  myhandler(int signum){
   switch(signum){
      case SIGINT:
        printf("\nHey, I got SIGINT: %d\n\n",signum);
        break;
      case 3:
        printf("\nHey, I got SIGQUIT: %d\n\n",signum);
        break;
      case 20:
        printf("\nHey, I got SIGTSTP: %d\n\n",signum);
        break;
      case 8:
         printf("\nHey, I got SIGFPE: %d\n\n",signum);
         break;
      case 9:
        printf("\nHey, I got SIGKILL: %d\n\n",signum);
        break;
      case 19:
        printf("\nHey, I got SIGSTOP: %d\n\n",signum);
        break;
   }
}

int main(){
   signal(SIGINT,  myhandler);
   signal(SIGQUIT, myhandler);
   signal(SIGTSTP, myhandler);
   signal(SIGFPE,  myhandler);
   signal(SIGKILL, myhandler);
   signal(SIGSTOP, myhandler);
   while(1) {
	printf("I am in an infinite loop!\n");
	sleep(1);
   }
   return 0;
}
```
- Note that in above signal 9 (`SIGKILL`) and 19 (`SIGSTOP`) cannot be caught
- Example
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#define TOTAL 5

void  myhandler(int signum){
   static int count = 0;
   count++;
   printf("\nDon't do it again\n");
   fflush(stdout);
   if(count >= TOTAL){
       printf("Well, if you insist, do it again and I will die!\n");
       fflush(stdout);
       signal(SIGINT, SIG_DFL);
   }
}

int main(){
   signal(SIGINT,myhandler);
   while(1);
   return 0;
}
```
- Example:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
void sighup1(int signum){
  printf("This is HANDLER - I for SIGHUP\n");
}
void sighup2(int signum){
  printf("This is HANDLER - II for SIGHUP\n");
}

int main(){
   void (*old)(int);
   signal(SIGHUP, sighup1);
   sleep(3);
   raise(SIGHUP);
   old = signal(SIGHUP, sighup2);
   sleep(3);
   raise(SIGHUP);
   signal(SIGHUP, old);
   sleep(3);
   raise(SIGHUP);
   signal(SIGHUP, SIG_DFL);
   sleep(3);
   raise(SIGHUP);
   sleep(100);
   return 0;
}
```

## Avoiding race conditions using signal mask

- problem that may occur when handling a singal is occurrence of a second signal while handler function is executing
- process can temporarily prevent signals from being delivered by blocking/masking it, while it is doing something critical or while it is executing inside a signal handler
- every process has a signal mask that defines the set of signals currently blocked for that process
    * One bit for each possible signal
    * If bit is ON that signal is currently blocked
- Since it is possible for the number of signals to exceed tthe number of bits in an integer, POSIX.1 defines a data type called `sigset_t` that holds a signal set of a process
- when a process blocks a signal the OS doesn't deliver the signal until the process unblocks the signal; however, when a process ignores a signal, signal is delivered and the process handles it by throwing it away
- note: after a `fork()`, child process inherits its parent's mask

## Functions related to singal sets

- To create a process singla mask, need to create a variable type `sigset_t`
    * `sigemptyset()` initializes a signal set to contain no members
    * `sigfillset()` initializes a set to contain all signals
    * Individual signals can be added to a set using `sigaddset()` and removed using `sigdelset()`
- Two ways to initialize a signal set:
    1. Initially specifiy it to be empty with `sigemptyset()` and then add specified signals individually using `sigaddset()`
    2. Initially specify it to be full with `sigfillset()` and then delete specified signals indivdually using `sigdelset()`
- After creating signal mask we use `sigprocmask()` to set a new signal mask of a process
    * `int sigprocmask(int how, const sigset_t* nset, sigset_t* oset);`
    * Second argument specifies the new signal mask
        + If null, then signal mask is unchanged
    * Third argument will store the old mask of the process
        + Useful when we want to restore the previous masking state once we're done with our critical section
    * First argument `how` determines how process signal mask will be changed. It can have three values:
        1. `SIG_BLOCK`: set of blocked signals is the union of `nset` and `oset`
        2. `SIG_UNBLOCK`: signals in `nset` are removed from current set of blocked signals
        3. `SIG_SETMASK`: set of blocked signals is set to `nset`
- Example:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(){
   sigset_t newset, oldset;
   // unmask all signals
   sigemptyset(&newset);
   // Masking SIGINT
   sigaddset(&newset, SIGINT);
   // Set current process mask to newset
   sigprocmask(SIG_SETMASK, &newset, &oldset);
   int i = 0;
   for(i=1; i<=10; i++){
	printf("I am masking SIGINT for 10 seconds!\n");
	sleep(1);
  }
  // Now we unmask SIGINT and it is delivered
  // The next print statement will not even get a chance to run if
  // SIGINT was delivered earlier
  sigprocmask(SIG_SETMASK, &oldset, NULL);
   for(i=1; i<=10; i++){
	printf("Now I am having the old sigset without any mask\n");
	sleep(1);
  }
   return 0;
}
```

## Limitations of using signal() system call

- Using `signal()` system call, we cannot determine the current disposition of a signal without changing the disposition
    * Example: if we want to determine the current disposition of `SIGINT`, we can't do it without changing the current disposition
- If we use `signal()`, to register a handler for a signal, it is possible that after we entered the signal handler, but before we maknaged to mask all the signals using `sigprocmask()` we receive another signal which will be called
- There are a lot of variations in the behavior of `signal()` call across unix implemnetations
- `sigaction()` is somewhat more complex to use than `signal()`, but it gives us the following advantages over `signal()`:
    1. allows us to retrieve the disposition of a signal without changing it
    2. Allows us to set various attributes controlling precisely what happens when a signal handler is invoked
    3. more portable than `signal()`
- First argument `signnum` identifies the signal whose disposition we want to retrieve or change
- Second argument `newact` is a pointer to a structure specifying a new disposition for the signal
    * If we are interested only in finding the existing disposition of the signal, then we vcan specify NULL for this argument
- Third argument `oldact` is used to return information about the singal's previous disposition
    * If we are not interesxted in this information then we can specify NULL for this argument
- Example of using `sigaction` to mask:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(){
 //signal(SIGINT,SIG_IGN);
 //signal(SIGFPE, SIG_IGN);
struct sigaction newact;
newact.sa_handler = SIG_IGN;
newact.sa_flags = 0;
sigemptyset(&newact.sa_mask);
sigaction(SIGINT, &newact, NULL);
sigaction(SIGFPE, &newact, NULL);


 while(1) {
   printf("I am in an infinite loop!\n");
   printf("You can't kill me by SIGINT <2> or SIGFPE <8>\n");
   sleep(2);
 }
 return 0;
}
```
- Example:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
void  myhandler(int signum){
   printf("Hey, I got signal: %d\n",signum);
   for(int i=1; i<=10; i++){
	printf("I am masking SIGINT for 10 seconds!\n");
	sleep(1);
   }
   printf("Done with the handler function and falling back to main() after 2 secs\n\n");
   sleep(2);
}

int main(){
   struct sigaction newact;
   newact.sa_handler = myhandler;
   newact.sa_flags = 0;
   sigfillset(&newact.sa_mask); // Masks all signals so that when handler is executing, all signals will be masked (once handler completes, signals will be delivered)
//   sigemptyset(&newact.sa_mask);
   sigaction(SIGINT, &newact, NULL);

   while(1) {
	printf("I am main() in an infinite loop!\n");
	sleep(1);
   }
   return 0;
}
```