# Lecture 13

## Repositioning CFO of an opened file

## lseek() system call

- `off_t lseek(int fd, off_t offset, int whence);`
- For each open file the kernel records a file offset i.e., current file offset (CFO) which is in the system wide file table
    * This is the location in the file at which the next `read()` or `write()` will commence
    * The file offset is expressed as an ordinal byte position relative to the start of the file
    * The first byte of the file is at offset 0
- The file offset is set to point to the start of the file when the file is openeed (unless `O_APPEND` is specified)
    * Automatically adjusted by each subsequent call to `read()` or `write()` so that it points to the next byte of the file after the bytes just read or written
    * Successive `read()` and `write()` calls progress sequentially through a file
- `lseek()` system call adjust the file offset of the open file referred to by the file descriptor `fd` according to the values specified in `offset` and `ehence`
    * On success, returns the resulting offset location and `-1` on failure

## Interpreting whence argument of lseek()

- Consider linear view of the file
    * File containing n bytes of data
        + 0 (`SEEK_SET`)
        + 1
        + ...
        + `SEEK_CUR` (`whence` value)
        + ...
        + `n-2`
        + `n-1` (`SEEK_END`)
    * Hole past EOF
        + `n`
        + `n+1`
        + ...
- `posn = lseek(fd, 54, SEEK_SET)`
    * Move 54 positions up from `SEEK_SET`
- `posn = lseek(fd, +/-54, SEEK_CUR)`
    * Move 54 ahead or behind from `SEEK_CUR`
- `posn = lseek(fd, +/-54, SEEK_END)`
    * Note: it is valid to move past EOF to create a hole for later insertion of data

## Example lseek

- Consider:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
extern int errno;
int  main(){
    // cant lseek the keyboard (standard input)
   int rv = lseek(0, 54, SEEK_SET);
   if (rv == -1){
      printf("Cannot seek\n");
      exit(errno);
   }
   else
      printf("seek OK\n");
   return 0;
}
```
- Above returns return code of 29
- `man errno` to see what 29 stands for Illegal Seek

## Example lseek 2
```
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

int main(){
//create a file and check the value of fd
   remove("f1.txt");
   int fd = open("f1.txt",O_RDWR|O_CREAT|O_TRUNC,0622);
   printf("open() returned fd= %d\n", fd);

//check and print value of cfo
   int cfo = lseek(fd, 0, SEEK_CUR);
   printf("Location of CFO= %d\n", cfo);

//write and check the value of cfo
   write(fd, "abcde", 5);
   cfo = lseek(fd, 0, SEEK_CUR);
   printf("Location of CFO after writing ""abcde""= %d\n", cfo);

//move the cfo 100 bytes ahead the EOF
   lseek(fd, 100, SEEK_END);
   cfo = lseek(fd, 0, SEEK_CUR);
   printf("Location of CFO after lseek(fd, 100, SEEK_END)= %d\n", cfo);

//let us write and check the value of cfo
   write(fd, "ABCDE", 5);
   cfo = lseek(fd, 0, SEEK_CUR);
   printf("Location of CFO after writing ""ABCDE""= %d\n", cfo);
   return 0;
}
```
- `ls -l f1.txt` will show that our file size is 110 bytes and permission is rw which corresponds to `umask` of `0022`
- `cat f1.txt` shows `abcdeABCDE`
- `od -c f1.txt`: octal dump shows all bytes including null entries `\0` where we skipped
```
0000000 a b c d e \0 \0 \0 \0 \0 \0
...
0000100 \0 \0 \0 \0 \0 A B C D E
```

## Example lseek 3
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]){
   int holes = atoi(argv[1]);
	int fd = open("filewithholes",O_CREAT|O_WRONLY|O_TRUNC, 0644);
	write(fd, "PUCIT", 5);
	for(int i = 0; i < holes; i++){
		lseek(fd, 10, SEEK_CUR);
		write(fd, "PUCIT", 5);
	}
	close(fd);
   return 0;
}
```

## Misc File Related System Calls

- Rename a file or directory with `rename()` library function
- Remove is a library call that deletes a name from file system
    * It calls `unlink()` for files and `rmdir()` for directories
    * If any process has this file open currently, the file won't be actually erased until the last process holding it open closes it
    * Until then it will be removed from the directory i.e., `ls` won't show it but not from disk
- When file is deleted, OS kernel performs following tasks:
    1. Frees inode number associated with that file
    2. Frees all data blocks associated with that file and add them to list of free blocks
    3. Delete entry from directory containing that file
- Metadata of file is still there in inode block and data of file in its data blocks
    * You just need to know how to access those blocks

## Symlink and link function

- The `link()` and `symlink()` functions are used to cerate hard link and soft link to a file

## chown, fchown and lchown function

- The system calls change owner and group of file specified by path or file descriptor
- If owner or group is specified as `-1` then ID is not changed
- Only a process with super user privileges can use these functions to change any file UID or GID
- However, if a process effective UID matches a file UID and its effective GID the process can change the file GID only
- `lchown()` is like `chown()` but does not dereference symbolic links

## chmod and fchmod system call

- These two functions allow us to change file access permissions for an existing file
- `chmod` function operates on the specified file whereas the `fchmod` operates on a file that has already been opened using its file descriptor
- The mode is the same as discussed in the flags argument of `open()`

## umask function

- `umask()` function sets the file mode creation mask for the process and returns its previous value
- Remember the mask value of a process is the same as that of its creating shell (i.e., its parent)
- The file mode creation mask is used whenever the process creates a new file or a new directory

## access() file system

- `access()` system call determines if calling process has access permission to a file and it can also check for file existence
- Mode argument is a bit mask consisting of one or more of the permission constants shown below:
    * `R_OK` to test read permission
    * `W_OK` to test write permission
    * `X_OK` to test execute permission
    * `F_OK` to test existence of file
- If process has all specified permission then return value is `0`; otherwise return value is `-1` and sets `ERRNO` to `EACCES`
- `open()` system call performs its access tests based on the EUID and EGID while `access()` system call bases its tests on the real UID and GID
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
//#include <fcntl.h> // if you are using constant O_RDONLY
//#include <sys/stat.h>
int main(int argc, char* argv[])
{
   if(argc != 2){
      fprintf(stderr, "Incorrect number of arguments\n");
      exit(1);
   }
   // Check if this file exists or not
   if (access(argv[1],F_OK) == 0)
      printf("This file exist\n");
   else{
      printf("This file do not exist\n");
      exit(1);
   }
   if (access(argv[1], R_OK) == 0)
      printf("You have read access to  this file\n");
   else
      printf("You do not have read access to this file\n");

   if (access(argv[1], W_OK) == 0)
      printf("You have write access to  this file\n");
   else
      printf("You do not have write access to this file\n");

   if (access(argv[1],X_OK) == 0)
      printf("You have execuete access to  this file\n");
   else
      printf("You do not have execute  access to this file\n");

   exit (0);
}
```

## I/O Redirection using dup()

- `dup()` call takes `oldfd` an open file descriptor and returns a new descriptor that refers to the same open file descriptor
- The old and new file descriptors point to the same entry in the system wide file table
    * After a successful return from these function, old and new fd's can be used interchangeably
- The new descriptor is guaranteed to be the lowest unused file descriptor
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
int main(){
   int fd1, fd2, n;
   char buff[10];
   fd1 = open ("abc.txt", O_RDONLY);
   fd2 = dup(fd1);
   //reading via fd1
   n = read (fd1, buff, 5);
   write(1, buff, n);
   //reading via fd2
   n = read (fd2, buff, 5);
   write(1, buff, n);
   //reading via fd1
   n = read (fd1, buff, 5);
   write(1, buff, n);
   return 0;
}
```
- In above example we see reading from `fd1`, `fd2` then `fd1` again has read the file continuously which highlights the fact both file descriptors are pointing to the same entry in the system wide file table

## Facts about I/O redirection on the shell

- Running just `cat` will result in a file descriptor process table like:
    * 0 to stdin
    * 1 to stdout
    * 2 to stderr
- Above just takes input from stdin via keyboard until press control-D for EOF
- Running `cat 0< f1.txt 1> f2.txt 2>&1` results in:
    * 0 to `f1.txt`
    * 1 to `f2.txt`
    * 2 to `f2.txt`
- Note: in above no arguments are passed to `cat` you are just redirecting I/O

## dup() system call

- We know that `dup()` guarantees that new descriptor returned is the loweest unused file descriptor
- If we run the following lines of code, `open` call will return 3, `dup` call will return the lowest unused descriptor which will be zero
    * Finally descriptor zero points to the opened file instead of stdin
    * Program:
    ```
    fd = open(...);
    close(0);
    newfd = dup(fd);
    ```
- To make above code simpler, and to ensure we always get the file descriptor we want, we can use `dup2()`
- `dup2()` system call makes a duplicate of the file descriptor given in `oldfd` using the descriptor number supplied in the `newfd`
- If file descriptor in `newfd` is already open `dup2()` will close it first
- We can simplify preceding calls to `close(0)` and `dup(fd)` on previous slide to following: `dup2(fd, 0)`
- A succecssful `dup2()` call returns the number of duplicate descriptor i.e., the value passed in `newfd`
- If `oldfd` is a valid file descriptor and `oldfd` and `newfd` have same value then `dup2()` does nothing; `newfd` is not closed and `dup2()` returns the `newfd`

## Example: Input Redirection

- Method 1: close-open
```
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
int main(){
   char	line[100];
/* read and print one line from stdin */
   fgets(line, 100, stdin );
   printf("%s", line);
/* redirect stdin to passwd file using close-open method */
   close(0);
   int fd = open("/etc/passwd", O_RDONLY);
/* read and print one line from stdin again*/
   fgets(line, 100, stdin);
   printf("%s", line);
   return 0;
}
```
- Method 2: open-close-dup-close
```
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
int main(){
   char	line[100];
/* read and print one line from stdin */
   fgets(line, 100, stdin );
   printf("%s", line);
/* redirect stdin to passwd file using open-close-dup-close*/
   int fd = open("/etc/passwd", O_RDONLY);
   close(0);
   int newfd = dup(fd);
   close(fd);
/* read and print one line from stdin again*/
   fgets(line, 100, stdin);
   printf("%s", line);
   return 0;
}
```
- Method 3: open-dup2-close
```
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
int main(){
   char	line[100];
/* read and print one line from stdin */
   fgets(line, 100, stdin );
   printf("%s", line);
/* redirect stdin to passwd file using open-dup2-close*/
   int fd = open("/etc/passwd", O_RDONLY);
   int newfd = dup2(fd, 0);
   close(fd);
/* read and print one line from stdin again*/
   fgets(line, 100, stdin);
   printf("%s", line);
   return 0;
}
```

## fcntl() system call

- `int fcntl(int fd, int cmd, long arg)`
- `fcntl()` system call can be used instead of `dup()` to return a duplicate file descriptor of an already open file
- Second argument passed to `fcntl()` for this purpose is `F_DUPFD`
    * It will return the lowest numbered available file descriptor greater than or equal to the third argument
- `fcntl()` system call can be used to get the file status flags
    * For example, suppose you have opened a file and want to check the file access mode flags
    * Second argument passed to `fcntl()` for this purpose is `F_GETFL` and the third argment is ignored
    * It will return the file access mode and file status flags in an integer variable which when bitwise anded with `O_ACCMODE` constant will tell you about the permissions
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
int main(int argc, char * argv[]){
   int accmode, flags;
   int fd = open(argv[1], O_RDONLY);
   flags = fcntl(fd, F_GETFL, 0);
   flags = flags & O_ACCMODE;
   if (flags == O_RDONLY) printf("read only\n");
   else if (flags == O_WRONLY) printf("write only\n");
   else if (flags == O_RDWR) printf("read write\n");
   else printf("Unknown access mode\n");
   return 0;
}
```
- `O_APPEND` flag used to ensure that each call to `write()` implicitly includes an `lseek` to the end of file
- Kernel combines `lseek()` and `write()` in a atomic operation
- Suppose you forgot to set this flag while making `open()` call
- now if you have already opened a file and want to set `O_APPEND` flag, you can do that  with `fcntl()` system call
- `O_SYNC` flag can also be set in same manner as above

## File/Record Locking

- Types of locking mechanisms:
    1. Advisory locks:
        * Kernel maintains knowledge of all files that have been locked by a process
        * But it does not prevent a process from modifying the file
        * The other process can check before modifying that the file is locked by some other process
        * Advisory locks require proper coordination between processes
    2. Mandatory locks
        * Strict implications in which kernel checks every read and write request to verify that the operation does not interfgere with a lock held by a process
- Locking in most UNIX machines is by default advisory
- Mandatory locks are also supported but requires special config
- Types of advisory locks:
    1. Read locks/shared locks
        * Locks in which you can read but if you want to write you will have to wait for everyone to stop reading
        * multiple read locks can co-exist
    2. Write locks/exclusive locks
        * Locks in which there is a single writer
        * Everyone else has to wait for doing anything else (reading or writing)
        * Only one write lock can exist at a time

## fcntrl() for file/record locking

- `fcntl()` system call can be used for read/write locks on a complete file or part of file
- To lock a file second argument to `fcntl()` should be `F_SETLK` for a non-blokcing call or `F_SETLKW` for a blocking call
- Third argment is a pointer to a variable of type `struct flock`
- Locks acquired using `fcntl()` are not inhererted across `fork()` but are preserved across `execve()`
- Example:
```
#include <stdio.h>
#include <stdlib.h> // for exit
#include <unistd.h> //for sleep
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
int main(){
   int fd = open("fcntl_lock.c", O_WRONLY);
   struct flock lock;
   lock.l_type = F_WRLCK;
   lock.l_whence = SEEK_SET;
   lock.l_start = 0;
   lock.l_len = 0;
   lock.l_pid = getpid();
   int rv = fcntl(fd, F_SETLK, &lock);
   if (rv == -1){
      printf("Lock can't be acquired\n");
      exit(1);
   }
   printf("File is successfully locked ...\n");
   while(1){}
}
```