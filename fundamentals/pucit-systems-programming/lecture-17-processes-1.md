# Lecture 17

## Processes vs Files

- Everything in Linux is either a process or a file
- `ps` to show process status in user space for current user
    + `ps -a` to show processes being run by all users in other terminals
    + `ps -l` to show different attributes of a process
        * Process uniquely identified by PID
- `ls` shows contents of filesystem
    + `ls -a` to show
    + `ls -l` to show long listing of current working directory
    + `ls -i` to show unique identifier for file (inode)
- Kernel keeps tracks of:
    + Which files are occupying which disk blocks
    + Which processes are occupying which pages of memory
- Previously showed format of file on disk
    + `0xc0000000` is where user stack ends and kernel virtual memory begins
    + `0xffffffff` is where kernel virtual memory ends foor 32-bit machine
    + Kernel virtual
        * Kernel code and data structure (same for every process)
        * Process specific data structures (different for every process)
            + Tells kernel about state of the process
            + Different resources process is holding e.g., open files
            + List of child and sibling processes
            + Owner of process
- Dig into kernel data structures
    + `uname -r` to check version of kernel
    + `sudo apt-get install linux-headers-<version of kernel>`
    + `cd /usr/src/linux-headers-<version of kernel>`
    + `cat fs.h` and search for `struct inode` and `struct file` for file management
    + `cat sched.h` and search for `struct task_struct` to show what is in process specific data structures in kernel virtual memory
        1. Process identification
            * PID, PPID
            * UID, GID
            * EUID, EGID
            * Saved SUID, SGID
            * File system UID, GID
        2. Process state information
            * User visible registers
            * Control and status registers
        3. Process control information
            * Scheduling info
            * Privileges info
            * Memory management ifo
            * Resouorce ownership and utilization
            * IPC
- `top` to monitor CPU usage in real time
    * Total processes running, sleeping stopped
    * Percentage of CPU used
    * By process info with most CPU intensive processes at the top
- `top` gets information from `/proc`
    * Contains `/proc/<pid>` which contains:
        + `cmdline` contains commands used to start process
        + `environ` contains environment variables
        + `limits` contains soft and hard resource limits
        + `maps` currently mapped memory regions
        + `sched` contains scheduling information
        + `stack` for stack status of process
        + `stat` contains process status to be read by programs
        + `status` contains same info as `stat` but in human readable form
        + `exe` softlink to process executable
        + `root` for root directory of process
        + `fd` contains symbolic link to each file descriptor
        + `tasks` directories for each thread in the process

## Accessing Process ID

- `pid_t getpid()`
- `pid_t getppid()`
- Above calls returns PID and PPID of process
- Each proces has a PID
- Linux kernel limits PIDs to being less than or equal to 32767
- Once it reaches that number, PID counter is reset to 300
- On 64-bit platforms, that can be adjusted to 2^22
- On shell you can get PID of shell via env var `$$` and parent ID via env var `PPID`
- Parent process found in 4th field of `/proc/PID/stat`
- `swapper` or scheduler is a system process having PID 0
    * Manages memoey allocation for processes
    * Swaps processes from run state to Ready Queue or other and may be to odisk
    * No program file for `swapper` in `/proc`
- `init` now `systemd` is a user proocess having PID of `1`
    * Invoked by the kernel at the end of booting process
- Page dameon now `kthreadd` is a system process having PID of `2`
    * Supports paging virtual memory system
- Example:
```
#include <stdio.h>
#include <unistd.h>
int main()
{
   printf("My PID is: %ld\n", (long)getpid());
   printf("My PPID is: %ld\n", (long)getppid());
   return 0;
}
```

## Real User ID and Group ID

- `uid_t getuid();`
- `gid_t getgid();`
- Real user ID and real group ID identifies user and group to owhich proocess belongs
- As part of login process, login shell gets its real UID and real GID from 3rd and 4th field of user's password record in `/etc/passwd`
- When new process is created (via `exec`) it inherits those IDs from parent
- Above two calls returns the real UID and real GID of current process

## Effective User ID and Effective Group ID

- `uid_t geteuid();`
- `gid_t getegid();`
- Effective IDs are used to determine a process's permission when accessing resources e.g., files, system V IPC objects which themselves have associated user and group IDs determining to which they belong
- Normally effective IDs have same values as real IDs but there are two ways using which effective IDs can take different values:
    1. By execution of programs having their SUID and SGID bit set
    2. Use of system calls e.g., `setuid()`, `setgid()`, etc

## Saved Set User ID and Saved Set Group ID

- These two IDs are designe for use with executable proograms having their SUID and SGID bit set
- When shell executes a program with SUID bit set then the effective IDs oof the process are made the same as the owner of the executable
- If SUID bit not set, then noo change is made to effective IDs of process i.e., they remain the same as real IDs of process
- EUID and EGID are copoied to the saved SUID and saved SGID respectively
- Example:
    * Process whose real, effective and saved set user ID are all `1000`
    * Process runs `exec` with SUID bit set and owned by root (`0`)
    * IDs of the child process will be:
        + real = 1000, effective = 0, saved = 0
- Example:
    * `ls -l /usr/bin/passwd`
    * Shows `-rwsr-xr-x` showing that it has its SUID bit set for owner (root)
    * When regular user executes this program, EUID becomes SUID for the process
    * EUID is used to check permissions when accessing resources
    * Therefore, when regular user executes this program, its EUID is set to the SUID owner of the executable (root), and thus we are able to modify `/etc/shadow`
    * `find /usr/bin -perm /40000` to find similarly behaving programs

## Real Effective and Saved User IDs

- `getresuid()` and `getresgid()` returns current values of calling proocess real, effective and saved user/grooup IDs in the locations pointed by these arguments
- On success `0` is returned
- On error `-1` is returned and `errno` is set appropriately
- Only error is `EFAULT` i.e., one of the arguments specified an address outside calling process's address space

## Other IDs

- Filesystem user and group IDs rahter that effective user and group IDs that are used to determine permission when performing filessytem operations e.g., opening file, changing file ownership, modifying file permission
- Supplementary grop IDs are set of additional groups `/etc/group` to which a process belongs
- A login shell obtain these from the `/etc/group` file while a new process inherits these IDs from its parent

## Accessing PIDs Examples

- Program:
```
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
int main()
{
   uid_t ruid, euid, suid;
   getresuid(&ruid, &euid, &suid);
   printf("My Real user-ID is: %ld\n", (long)ruid);
   printf("My Effective user-ID is: %ld\n", (long)euid);
   printf("My Saved Set-user-ID is: %ld\n", (long)suid);

   gid_t rgid, egid, sgid;
   getresgid(&rgid, &egid, &sgid);
   printf("My Real group-ID is: %ld\n", (long)rgid);
   printf("My Effective group-ID is: %ld\n", (long)egid);
   printf("My Saved Set-group-ID is: %ld\n", (long)sgid);
   return 0;
}
```

## Modifying Effective IDs

- Changes the effective IDs and possibly the real and saved-set IDs of the calling process to the given value by argument
- Rules that govern changes that a proocess can make to its IDs using `setuid()` and `setgid()`:
    1. When unprivileged process calls `setuid()` only effective user ID of process is changed; can only be changed t othe same values as either real user ID or saved set user-ID
    2. When privileged process calls `setuid()` with non-zero oargument then real, effective and saved set user ID are all set t othe specified value in `uid/gid` argument; note that this is a one way trip i.e., subsequently the process cannot use `setuid()` to reset identifiers back to 0
- `setresuid()` and `setresgid()` to change real, effective and saved IDs in one call
    * A regular user cannot change their real ID, only the effective ID to the SUID
- Example:
```
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
int main()
{
   uid_t ruid, euid, suid;
   getresuid(&ruid, &euid, &suid);
   printf("My Real user-ID is: %d\n", (long)ruid);
   printf("My Effective user-ID is: %d\n", (long)euid);
   printf("My Saved Set-user-ID is: %d\n\n\n", (long)suid);

   int rv = setresuid(100, 2000, 3000);
   if (rv == -1){
      printf ("Error in setting ID\n");
      exit(1);
   }

   getresuid(&ruid, &euid, &suid);
   printf("\n\nAfter setuid(2000) the IDs are:\n");
   printf("My Real user-ID is: %d\n", (long)ruid);
   printf("My Effective user-ID is: %d\n", (long)euid);
   printf("My Saved Set-user-ID is: %d\n", (long)suid);
   return 0;
}
```

## Process Creation

- Process creation using `fork()`
    * `pid_t fork();`
    * `fork()` system call allows one process, the parent to create a new process, the child
    * System call in which it is called once but returned twice
        1. Once to the parent which gets PID of child
        2. Once to ochild which gets 0 if sucess
    * Once call returns, both parent and child processes continue execution concurrently from next line of code
    * Child process is a clone of parent and obtains coopies of parents stwack, data, heap and text segments
    * PIDs are allocated sequentially to new child process so effectively unique
    * On failure, `-1` returned to parent context, no child process created and `errno` set appropriately
- Three main reasons of `fork()` failure:
    1. `EAGAIN`: system imposed limit on number of processes
        * Number of processes for one user reached
        * Kernel limit on number of proocesses reached
    2. `ENOMEM`: failure to allcoate necessary kernel structures due to lack of memory
    3. `ERESTARTNOINTR`: system call interrupted by a signal and will be restarted
- Why `fork()` returns twice:
    * Return value oot the child proocess is 0 because 0 is the ID of swapper process oonly and a child process can always call `getppid()` too obtain parent PID
    * Return value of parent process is PID of child because a process can have more than one child and there is noo function that allows a process to obtain PIDs of its children
- Two main uses of `fork()`
    1. Process wants to duplicate itself so parent and child each can execute different sections of code cooncurrently
        * Example: network server
            + Parent waits for service request from client
            + Request arrives, parent calls `fork` and lets child handle request
            + Parent waits for next request
    2. When process wants to oexecutes a diffrent program
        * Common for command shells where child does `exec()` right after returning from `fork()`
- Race condition after a `fork()`
    * After a `fork()` it is indeterminate which process (parent or child) will execute
    * On multi-processor system they may both get simultaneous access to the CPU
    * In most cases, parent will execute first
    * In Linux 2.6.32 since parent's state is already active in CPU and its memory management info is already cached in the hardware TLB, running parent first should result in better performance
- Attributes inhereted by child:
    * Real, effective, saved UIDs/GIDs
    * Open file descriptors (PPFDT)
    * Env vars
    * Present working directory
    * Nice value
    * File mode creation mask (umask)
    * Signal mask and signal disposition
    * Attached shared memory segments
- Difference between parent and child after `fork()`
    * Different PID and PPID
    * Return value from fork
    * Childs CPU time reset to 0
    * File locks held by parent are not inherited
    * Set of pending alarms/signals in the parent are cleared in the child
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main()
{
   int cpid = fork();
   if (cpid == 0)
       printf("Hello I am child\n");
   else
       printf("Hello I am parent\n");
   return 0;
}
```
- Example: both child and parent executing concurrently:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main()
{
   int cpid = fork();
   if (cpid == 0)
      while(1) putchar('x');
   else
      while(1) putc('o', stdout);
   return 0;
}
```
- `ps -a` will show two `a.out` executing concurrently
- Example: show both parent and child have its own vars
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main()
{
   int i,cpid, ctr=0;
   cpid = fork();
   if (cpid == 0){
      ctr = 100;
      for (i = 0; i< 3; i++)
         printf("Child counter is:%d\n", ctr++);
   }
   else{
      for(i = 0; i< 3; i++)
         printf("Parent counter is:%d\n",ctr++);
   }
   return 0;
}
```
- Example: `fork()` called multiple times:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
   if(argc!=2){
      printf("Must enter one agrument (an integer)\n");
      exit(1);
   }
   int n = atoi(argv[1]);
   int i;
   for (i=1;i<=n;i++)
      fork();
   printf("PUCIT\n");
   exit(0);
}
```
- Example: PPFDT is inherited by child, and they share file offset since FD point to same system wide file table entry
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>

int main()
{
   int fd;
   char msg1[] = "System Programming is fun with Arif Butt\n";
   char msg2[] = "This is parent\n";
   char msg3[] = "This is child\n";
   fd = open("f1.txt", O_CREAT | O_WRONLY | O_TRUNC, 0644);
   if(fd==-1){
      printf("open failed\n");
      exit(1);
   }
   write(fd, msg1, strlen(msg1));
   int cpid = fork();
   if (cpid == 0)
      write(fd, msg3, strlen(msg3));
   else
      write(fd, msg2, strlen(msg2));
   close(fd);
   return 0;
}
```

## Process Trees, Chains and Fans

- Process tree
    * Parent forks once and then child call next fork and so on
    * Example:
    ```
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>

    int main(int argc, char *argv[])
    {
    if(argc != 2){
        fprintf(stderr, "Incorrect number of arguments. Pl pass one integer\n");
        return 1;
    }
    pid_t cpid;
    int n = atoi(argv[1]);
    int i;
    for (i=1;i<=n;i++){
        fork();
    }
    //   fflush(0);
    fprintf(stderr,"PID=%ld, PPID=%ld\n",(long)getpid(), (long)getppid());
    while(1);
    return 0;
    }
    ```
- Process chain
    * Parent forks once and the child calls next fork and so on
    * Example:
    ```
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>

    int main(int argc, char *argv[])
    {
    if(argc != 2){
        fprintf(stderr, "Incorrect number of arguments. Pl pass one integer\n");
        return 1;
    }

    int n = atoi(argv[1]);
    int i;
    for (i=1;i<=n;i++)
        if(fork() != 0)//parent should break
            break;
    fprintf(stderr, "PID=%ld, PPID=%ld\n",(long)getpid(), (long)getppid());
    while(1);
    return 0;
    }
    ```
- Process fan:
    * Parent is responsible for every fork, child processes will break while parent process will iterate again
    * Example:
    ```
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <sys/types.h>

    int main(int argc, char *argv[])
    {
    if(argc != 2){
        fprintf(stderr, "Incorrect number of arguments. Pl pass one integer\n");
        return 1;
    }

    int n = atoi(argv[1]);
    int i;
    for (i=1;i<=n;i++)
        if(fork() == 0){
            break;
        }
    fprintf(stderr, "PID=%ld, PPID=%ld\n",(long)getpid(), (long)getppid());
    while(1);
    return 0;
    }
    ```