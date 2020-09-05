# Lecture 15

## OS Configuration Files

- User configuration files
    * `~/.bashrc`
    * `~/.bash_history`
    * etc
- System admin files
    * `/etc/passwd`
    * `/etc/shadow`
    * etc
- Kernel configuration files
    * `/proc/version`
    * `/proc/cpuinfo`
    * `/proc/filesystems`
    * `/proc/sys/kernel/version`
    * etc
- Network configuration files
    * `/etc/network/interfaces`
    * `/etc/hosts`
    * `/etc/resolv.conf`
    * `/etc/services`
    * `/etc/protocols`
- Miscellaneous configuration files
    * `/etc/fstab`
    * `/etc/localtime`
    * etc
- User program configuration files
    * `/etc/ssh/sshd_config`
    * `/etc/apache2.conf`
    * etc

## UNIX who utility

- Default `who` behavior is to display list of currently logged in useres, one on each line
```
<user name> <device e.g., tty, pts> <login time> <user ip>
```
- Information is derived from `/var/run/utmp`
- `who` performs the following:
    1. Opens `/var/run/utmp`
    2. Reads `utmp` data structure until end of file
    3. Display the required fields
    4. Go to step 2
    5. Close file `/var/run/utmp`
- `utmp` structure
```
struct utmp{
    char   ut_user[32]; // user login name
    char   ut_line;     // terminal name
    time_t ut_time;     // logged in time
    char   ut_host;     // host name
    int    ut_type;     // type of login
};
```

## Version 1

- Program
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <utmp.h>
#include <fcntl.h>

void show_info(struct utmp*);
int main(){
    // Open utmp in read only loop
   int fd = open("/var/run/utmp", O_RDONLY);
   if (fd == -1 ){
	   perror("Error in opening utmp file");
	   exit(1);
   }
   struct utmp rec;
   int reclen = sizeof(rec);
   // Read syscall to read record utmp structure one at a time
   while (read(fd, &rec, reclen) == reclen)
	   show_info(&rec);
   close(fd);
	return 0;
}

void show_info(struct utmp *rec){
	printf("%-10.10s   ", rec->ut_user);
	printf("%-10.10s   ", rec->ut_line);
	printf("%-10.10d", rec->ut_time);
   printf("   (%s)", rec->ut_host);
	printf("\n");
}
```

## Version 2

- Convert epoch to date time string
- Program
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <utmp.h>
#include <fcntl.h>
#include <time.h>

void show_info(struct utmp*);
int main(){
   int fd = open("/var/run/utmp", O_RDONLY);
   if (fd == -1 ){
	   perror("Error in opening utmp file");
	   exit(1);
   }
   struct utmp rec;
   int reclen = sizeof(rec);
   while (read(fd, &rec, reclen) == reclen)
	   show_info(&rec);
   close(fd);
	return 0;
}

void show_info(struct utmp *rec){
	printf("%-10.10s   ", rec->ut_user);
	printf("%-10.10s   ", rec->ut_line);
   long time = rec->ut_time;
   // Convert epoch time to string via ctime
   char* dtg = ctime(&time);
	printf("%-15.12s", dtg+4);
   printf("   (%s)", rec->ut_host);
	printf("\n");
}
```

## Version 3

- Remove system users
- Need to check out the utmp header to find `utmp` struct parameter that indicates login type (in this case it is `ut_type`)
    * We find that `7` indicates a normal process so we will just filter for this
- Program
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <utmp.h>
#include <fcntl.h>
#include <time.h>

void show_info(struct utmp*);
int main(){
   int fd = open("/var/run/utmp", O_RDONLY);
   if (fd == -1 ){
	   perror("Error in opening utmp file");
	   exit(1);
   }
   struct utmp rec;
   int reclen = sizeof(rec);
   while (read(fd, &rec, reclen) == reclen)
	   show_info(&rec);
   close(fd);
	return 0;
}

void show_info(struct utmp *rec){
    // Perform the check here to ensure utmp structure is for a regular process
   if(rec->ut_type != 7)
      return;
	printf("%-10.10s   ", rec->ut_user);
	printf("%-10.10s   ", rec->ut_line);
   long time = rec->ut_time;
   char* dtg = ctime(&time);
	printf("%-15.12s", dtg+4);
   printf("   (%s)", rec->ut_host);
	printf("\n");
}
```

## What is buffering

- System calls are expensive because there is a switch from user to kernel space then has to switch back to user space
- Assume you write a program that performs `read()` system call one character at a time for 1000 times
    * This would require 1000 mode switches
- On the contrary if we `read()` 100 bytes at a time, we would only require 10 mode switches improving performance
- Consider program that copies file one character at a time:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#define BUFSIZE 1024
int main(int argc, char *argv[]){
   if (argc != 3)	{
      printf("Invalid number of arguments.\n");
      exit(1);
   }
   int srcfd = open (argv[1], O_RDONLY);
   int destfd = open(argv[2],O_CREAT|O_RDWR|O_TRUNC, 00600);
   char buff[BUFSIZE];
   int n = 0;
   for(;;){
   n = read (srcfd, buff, BUFSIZE);
   if (n <= 0){
      close(srcfd);
      close(destfd);
      return 0;
   }
   write(destfd, buff, n);
   }
   close(srcfd);
   close(destfd);
   return 0;
}
```
- It takes much longer with smaller e.g., `1` buffer size due to the mode switches involved
- If buffering in the user space works so well, does the kernel perform buffering as well?
    * When you tell the kernel to read even a single byte from a file on disk, it reads blocks from the hard disk to the kernel buffer, and gives the user process what it requested
    * If the process asks for more characters later from the same file, the kernel just returns more data from the kernel space to process space (via the buffer)
    * When kernel buffer goes empty, it puts the process to sleep and adds the next needed disk block to its shopping list and continues the execution of other processes
    * Some time later it goes back to disk to get the requested data on its shopping list and starts servicing those processes
- In summary:
    * A `read()` system call copies data from kernel space buffer to user space buffer
    * A `write()` system call copies data from user space buffer to kernel space buffer
- Transferring data from kernel buffer and disk is different than read/write calls
- Consequences of kernel buffering
    1. Faster disk I/O
    2. Optimized disk writes
    3. Need to write buffers to disk before shutdown