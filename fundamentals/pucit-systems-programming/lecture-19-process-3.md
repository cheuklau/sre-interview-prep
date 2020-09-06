# Lecture 19

## exec() functions

- Process may overwrite itself with another executable image
- When process calls one of the six `exec()` functions, it is completely replaced by new program and new program starts executing its `main` function
- Five library functions of `exec` family and all are layered on top of the `execve()` system call
- There is no return after a sucessful `exec` call
- `exec()` functions return only if an error has occurred
    * Return value is `-1` and `errno` is set too indicate the error
- `execl` family
    * `execl()`, `execlp()`, `execle()`
    * First argument to this family of `exec()` calls is the name of the executable which on success overwrite the address space of the calling proocess with a new program from secondary storage
    * `l` means command line arguments to new program will be passed as a separated list of strings with `\0` at the end
    * `p` stands for path meaning program specified as the first argument should be searched in all directories listed in `PATH`
    * `e` stands for environment meaning after command line arguments program should pass an array of pointers to null terminated strings specifying the new env of the program to be executed
- `execv` family
    * `execv()`, `execvp()`, `execve()`
    * First argument is the name of executable which on success will overwrite the address space of calling program with a new program
    * `v` means command line arguments to these functioons will be passed as an array of pointers to null terminated strigns
    * `p` stands for path (same as previous)
    * `e` stands for environment (same as previous)
- Reasons of failure:
    * `EACCES`: specified proogram not a regular file or doesn't have execute permissions
    * `ENOENT`: specified program does not exist
    * `ENOEXEC`: specified proogram is not recognizable executable format
    * `ETXTBSY`: specified program is open for writing by another process
    * `E2BIG`: total space required by argument list and env list exceeds allowed max
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <wait.h>
int main(){
   int status;
   pid_t cpid = fork();
   if (cpid == 0){
      execlp("ls", "myls", "-l", "/home/", NULL);
      // This line should not be printed if execlp is successful
      printf("This line will not be printed\n");
   }
   else{
      wait(&status);
      printf("Hello I m Parent.\n");
   }
   return 0;
}
```
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <wait.h>
extern char ** environ;
int main(){
   int status;
   pid_t cpid = fork();
   if (cpid == 0){
      char *argv[]={"myls","-l","/home",'\0'};
      // Same as before but this takes an array of arguments
      execv("/bin/ls",argv);
      perror("exec failed");
  }
   else{
      wait(&status);
      printf("Hello I m Parent.\n");
   }
   return 0;
}
```
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <wait.h>
extern char ** environ;
int main(){
   int status;
   pid_t cpid = fork();
   if (cpid == 0){
       // Pass in shell environment variables
      execle("/usr/bin/gnome-calculator","mycalc",NULL, environ);
      perror("exec failed");
   }
   else{
      wait(&status);
      printf("Hello I m Parent.\n");
   }
   return 0;
}
```
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <wait.h>

int execute(char**);
int main(){
   char	*arglist[10];
   arglist[0] = "/bin/ls";
   arglist[1] = "-l";
   arglist[2] = "/home";
   arglist[2] = NULL;
   int rv = execute(arglist);
   return rv;
}

int execute(char *arglist[]){
   int status;
   pid_t cpid = fork();
   switch(cpid){
      case -1:
         perror("fork failed");
         exit(1);
      case 0:
         execvp(arglist[0], arglist);
         perror("execvp failed");
	      exit(1);
      default:
	      waitpid(cpid, &status, 0);
          // Shift by 8 bits to get the exit status
         status = status >> 8;
         printf("Child exited with status %d\n", status);
         return status;
   }
}
```

## Attributed inherited after fork() and exec() calls

- Process PIDs, `fork()`, `exec()`
    * PID, no, preserved
    * PPID, no, preserved
    * PGID, inherited, preserved
    * SID, inherited, preserved
    * Real IDs, inherited, preserved
    * Effective and saved SUIDs, inherited, preserved (can be changed)
    * Supplementary group IDs, inherited, preserved
- Process address space, `fork()`, `exec()`
    * Text segment, shared, no
    * Stack segment, inherited, no
    * Data and heap segments, inherited, no
    * Env var, inherited, depends on `exec` call
    * Memory mappings, inherited, no
    * Memory locks, no, no
- Files and directories, `fork()`, `exec()`
    * File descriptor table, inherited, preserved
    * Close-on-exec flag, inherited, preserved
    * File offsets, shared, preserved
    * Open file status flag, shared, preserved
    * Directory streams, inherited, no
    * Present working dir, inherited, preserved
    * File mode creation mask, inherited, preserved
- Scheduling and resoources, `fork()`, `exec()`
    * Nice value, inherited, preserved
    * Priority, inherited, preserved
    * Scheduling policy, inherited, preserved
    * Resource limits, inherited, preserved
    * Resource usage, no, preserved
    * CPU times, noo, preserved
    * Exit handlers, inherited, no

## Process Attribute Inheritance Example

- Program
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <wait.h>
void exit_handler(){
   printf("Exit handler\n");
}
int main(){
   atexit(exit_handler);

pid_t cpid = fork();
   if (cpid == 0){
      printf("This is child process.\n");
      exit(0);
   }
   else{
      wait(NULL);
      printf("This is parent process.\n");
      exit(0);
   }
}
```
- Program
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <wait.h>
void exit_handler(){
   printf("Exit handler\n");
}
int main(){
   atexit(exit_handler);

pid_t cpid = fork();
   if (cpid == 0){
      execlp("/bin/ls", "myls", "/home", '\0');
      printf("This is child process.\n");
      exit(0);
   }
   else{
      wait(NULL);
      printf("This is parent process.\n");
      exit(0);
   }
}
```

## Executing a Shell Command using system()

- `int system(const char* command)`
- Executes a command specified in `cmd` by calling `/bin/bash -c` and returns after command has been completed
- Return `-1` on error and return status of the `cmd` otherwise
- Main cost of `system()` is inefficiency
    * Executing a command using `system()` requires the creation of at least two processes:
        1. One for the shell
        2. Other for the command(s) it executes
- Example:
```
#include <stdlib.h>
#include <stdio.h>
int main(int argc, char* argv[]){
   system(argv[1]);
   printf("\nDone... Bye\n");
   exit(0);
}
```

## Implementing system () using exec()

- The `-c` optioon to `/bin/bash` provides an easy way to execute a string containing arbitrary shell command:
    * `/bin/bash -c "ls"`
- If there are arguments after the string, they are assigned too the positioonal parametrs starting with `$0`
- This to implement `system()`, we need to use `fork()` to create a child that does an `execl()` to the `bash` program
- Program
```
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int mysystem(char*);
int main(){
   printf("Running ls command using mysystem()\n\n");
   mysystem("ls -l /home");
   printf("\nDone... Bye\n");
   exit(0);
}
int mysystem(char * cmd){
   pid_t cpid = fork();
   switch(cpid){
      case -1:
	      perror("fork failed");
	      return -1;
      case 0:
	      execlp("/bin/bash", "mybash","-c", cmd, '\0');
	      perror("execlp() failed");
         return -2;
      default:
	      waitpid(cpid, NULL, 0);
	      return 0;
   }
}
```

## Process Groups, Sessions, and Coontrolling Terminals

- Illustartion of job control states
    1. Command : running in foreground
    2. Command & : running in background
    3. Termimation
    4. Suspended : stopped background
- `ctrl + c` : SIGINT to terminate
    * Go from `Command` to `Terminated`
- `ctrl + \` : SIGQUIT to terminate
    * Go from `Command` to `Terminated`
- `ctrl + z` : SIGTSTP to suspend in backgroound
    * Go from `Command` to `Suspended`
- `fg SIGCONT` to bring suspended process back to foreground
    * Go from `Suspended` to `Command`
- `bg (SIGCONT)` : Running in background
    * Go from `Suspended` to `Command &`
- `kill (SIGSTOP)`
    * Go from `Command &` to `Suspended`
- `fg SIGNCONT`
    * Go from `Command &` to `Command`
- `kill`
    * Go from `Suspend` to `Terminated`
    * Go from `Command &` to `Terminated`

## Process Groups, Session and Terminals

- Process group is set of one or more processes sharing the same PGID
    * Every process group has a Process Group Leader which is the process that creates the group who PID becomes the PGID of that group
        * Child process inherits parents PGID
        * Life time of a processor group starts when leader creates group and ends when last member process leaves the group
- Session is a collection of one or more process groups
    * Process's session membership is determined by its SID
    * Every session has a session leader which is the process that creates a new session and whose PID becomes the SID
    * At any point in time, one of the process groups in a sessioon is the foreground process group and others are background process groups
- Terminal
    * All processes in a session shares a controlling terminal which is established when a session leader first opens a terminal device
    * A session leader is the controlling process for the terminal
    * If a terminal disconnect occurs, kernel sends the session leader `SIGHUP` signal

## Relationships between PGs, Session and CT

- Consider following example:
```
echo $$
400
find / 2> /dev/null | wc -l &
[1] 659
sort < longlist| uniq -c
```
- In the above example we have:
    1. Controlling terminal
        * Foreground PGID = 660
        * Controlling SID = 400
    2. Session 400
        * Process group 400 (background process group)
            + `bash` (session leader, process group leader)
                - `PID=400`
                - `PPID=399`
                - `PGID=400`
                - `SID=400`
        * Process group 658 (background process group)
            + `find` (process group leader)
                - `PID=658`
                - `PPID=400`
                - `PGID=658`
                - `SID=400`
            + `wc`
                - `PID=659`
                - `PPID=400`
                - `PGID=658`
                - `SID=400`
        * Process group 660 (foreground process group)
            + `sort` (process group leader)
                - `PID=660`
                - `PPID=400`
                - `PGID=660`
                - `SID=400`
            + `uniq`
                - `PID=661`
                - `PPID=400`
                - `PGID=660`
                - `SID=400`
- Retrieving and changing process group
    * `getpgid()` returns process group ID of the process specified by `pid`
        + If `pid` is zero, PID of curretn process is used
    * `setpgid()` sets PGID of process specified by `pid` and `pgid`
    * `setpgid()` is used to move a process from one process group to another, both process groups must be part of same session
        * In this case, the `pgid` specifies an existing process group to be joined and the session ID of that group must match the session ID oof the joining process
    * `getsid()` returns session ID of process
    * `setsid()` creates a new session if the calling process is not a process group leader
        * Calling process is made the leader of the new sessioon i.e., set its SID is made the same as its PID
        * Calling process also becomes he process group leader of a new process group in the session i.e., its PGID is made same as its PID
        * Calling process will be the only process in the new process group and in the new session