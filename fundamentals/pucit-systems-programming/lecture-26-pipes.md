# Lecture 26

## Introduction to pipes

- `man 7 pipe`
- Pipes goes back to 3rd edition of unix in 1973
    * No name and can therefore be used only between related processes
    * Corrected in 1982 with addition of FIFOs
- Byte stream
    * Pipe is a byte stream i.e., there is no concept of message boundaries when using a pipe
    * Each read operation may read an arbitrary number of bytes regardless of the size of bytes written by the writer
    * Data passes thgrough pipe sequentially and bytes are read from a pipe in same order they are written
    * Not possible to randomly access data in a pipe using `lseek()`
- Pipes are unidirectional
    * Data can travel only in one direction
    * One end of the pipe used for writing and other for reading
- Reading from  a pipe:
    * When process reads bytes from a pipe, those bytes are removed (destructive read semantics)
    * By default when a process attempts to read from a pipe that is empty, the read call blocks until some bytes are written into the pipe
    * If write end of pipe is closed and a process tries to read, it will receive EOF character i.e., `read()` returns `0`
    * If two processes try to read from the same pipe, one process will get some of the bytes of the pipe and other process will get the other bytes
        + Unless two processes use some method to coordinate access to the pipe, the data they read are likely to be incomplete
- Writing to a pipe:
    * When a process tries to write to a pipe that is currently full, the `write(2)` call blocks until there is enough space in the pipe
    * If a process tries to write say 1000 byutes and there is room for 500 bytes only, the call waits until 1000 bytes of space are available
    * If read end of pipe is closed and a process tries to write, the kernel sends `SIGPIPE` to the writer process
- Size of pipe
    * If multiple processes are writing to a single pipe, then it is guaranteed that their data won't be intermingled if they write no more than `PIPE_BUF` bytes at a time
        + This is because wriitign `PIPE_BUF` number of bytes to a piep is an atomic operation
        + On Linux, value of `PIPE_BUF` is 4096
    * When writing more bytes than `PIPE_BUF` to a pipe, the kernel may transfer the data in multiple smaller pieces, appending further data as the reader removes bytes from the pipe
        + The `write()` call blocks until all of the data has been written to the pipe
    * When there is a single writer process this doesn't matter but in case of multiple writer processes, this may cause problems
- Creating a unix pipe
    * A pipe is crealed by calling `pipe()` system call
    * Creating a pipe is similar to opening two files
        + Succesful call to `pipe()` returns two open file descriptors in the array `fd`
            1. Contains the read descriptor of the pipe `fd[0]`
            2. Contains the write descriptor of the pipe `fd[1]`
    * As with any file descriptor, we can use the `read()` and `write()` system calls to perform I/O on the pipe
        + Once written to the write end of a piep, data is immediately available to be read from the read end
        + A `read()` from a pipe blocks if the pipe is empty
    * From an implementation point of view, a pipe is a fgixed-size main memory circular buffer created and maintained by the kernel
        + The kernel handles synchronization required for making the reader process wait when the pipe is empty and the writer process wait when pipe is full
- `pipe2()` system call can also be used
    + Second argument `flags` is used to control the attrivutes of the pipe descriptors
    + Zero in the flags make `pipe2()` behave like `pipe()` system call

## Use of a pipe in a single process

- Example:
```
int fd[2];
pipe(fd);
int cw = write(fd[1], msg, strlen(msg));
int cr = read(fd[0], buf, cw);
write(1, buf, cr);
```
- The PPFDT has:
    0. stdin
    1. stdout
    2. stderr
    3. `fd[0]`
    4. `fd[1]`
- Write descriptor of pipe writes to the write end of pipe via kernel call to `write()`
- Read descriptor of pipe reads from the write end of pipe via kernel call to `read()`

## Examples

- Example of single process pipe:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define SIZE  25
int main(){
   const char * msg = "Hello, World! (Using pipe) \n";
   char  buf[SIZE];
   memset(buf,'\0',SIZE);
//create a pipe
   int fd[2];
   int rv = pipe(fd);
   if (rv == -1){
	printf("\n Pipe failed");
	exit(1);
   }
//write data in the pipe using fd[1] that points to write end of pipe
   int cw = write(fd[1],msg, strlen(msg));
//read data from the pipe using fd[0] that points to read end of pipe
   int cr = read(fd[0], buf, cw);
//display the data on stdout
   write(1, buf, cr);
   while(1);
   return (0);
}
```
- `ls /proc/<pid>/fd/` will show additional `3` and `4` file descriptors pointing to the read and write ends of the pipe
- Example of pipe between parent and child:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define SIZE 1024
int main(){
   int fd[2];
   int rv = pipe(fd);
//create a child process
   pid_t cpid = fork();
//parent code (parent is writer process)
   if (cpid != 0) {
      close(fd[0]);
      const char * msg = "Welcome to Communication using pipes\n";
      write(fd[1], msg,strlen(msg));
      waitpid(cpid, NULL, 0);
      exit(0);
   }
//child code (child is reader process)
   else {
      close(fd[1]);
      char buff[SIZE];
      memset(buff, '\0',SIZE);
      fprintf(stderr,"Message sent from parent is: ");
      int n = read(fd[0],buff,SIZE);
      write(1,buff,n);
      exit(0);
   }
}
```
- In the above program:
    1. Parent creates a pipe resulting in PPFDT having `3` and `4` pointing to `fd[0]` and `fd[1]` i.e., the read and write ends of the pipe
    2. Parent calls `fork()` creating a child process which also copies the PPFDT
    3. If we want parent to be the writer and child to be the reader then:
        * Close `fd[1]` of the child that points to the write end
        * Close `fd[0]` of the parent that points to the read end
- Example of creating two pipes between parent and child allowing bidrectional communciation:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define SIZE 1024
int main(){
   int fd1[2];
   int fd2[2];
   pipe(fd1);
   pipe(fd2);
//create a child process
   pid_t cpid = fork();
//***Child will read from fd2[0] and write into fd1[1]
   if (cpid == 0) {
      close(fd1[0]);
      close(fd2[1]);
      char childbuff[SIZE];
      memset(childbuff, '\0',SIZE);
      const char *msgfromchild = "Zalaid Mujahid Butt";
//child receives a message from parent
      int n = read(fd2[0],childbuff,SIZE);
      printf("\nI am child.");
      printf("\nParent asked: ");
      fflush(stdout);
      write(1,childbuff,n);
//child sends a response to parent
      write(fd1[1],msgfromchild,strlen(msgfromchild));
      exit(0);
   }
//***Parent will write into fd2[1] and read from fd1[0]
   else {
      close(fd1[1]);
      close(fd2[0]);
      char parentbuff[SIZE];
      memset(parentbuff, '\0',SIZE);
      const char * msgfromparent = "What is your name child?";
//parent sends a message to child
      write(fd2[1], msgfromparent,strlen(msgfromparent));
//parent receives a message from child
      int n = read(fd1[0],parentbuff,SIZE);
      printf("\n\nI am parent, and have received my child's name.");
      printf("\nWelcome Mr. ");
      fflush(stdout);
      write(1,parentbuff,n);
      printf("\n");
	   exit(0);
   }
}
```
- Example that simulates `cat f1.txt | wc`
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int main(){
   int fd[2];
   pipe(fd);
   pid_t cpid = fork();
   if (cpid != 0){  //parent process
      dup2(fd[1], 1); //redirect stdout to write end of pipe
      close(fd[0]); //not required so better close it
      execlp("cat","mycat", "f1.txt", NULL);
   }
   else{  //child process
      dup2(fd[0], 0); //redirect stdin to read end of pipe
      close(fd[1]);  //not required so better close it
      execlp("wc","mywc", NULL);
   }
}
```
- In the above example:
    * `cat` process sets PPFDT `1` (`stdout`) to point to `f[1]` i.e., the write end of the pipe
    * `wc` process sets PFFDT `0` (`stdin`) to point to `f[0]` i.e., the read end of the pipe
    * Note: `dup1` is used to duplicate a file descriptor
- Example of doing a fan to pipe `man` to `grep` to `wc`
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int main(){
   int status;
   int fd1[2];
   int fd2[2];
   pipe(fd1);
   pipe(fd2);

//Parent do a first fork to execute man
   if (fork() == 0){
      dup2(fd1[1], 1);//redirect output of man
      close(fd1[0]);
      close(fd2[0]);
      close(fd2[1]);
      execlp("man","man", "ls", NULL);
   }
//Parent do a second fork to execute grep
   else if (fork() == 0){
      dup2(fd1[0], 0);//redirect stdin of grep
      dup2(fd2[1], 1);//redirect stdout of grep
      close(fd1[1]);
      close(fd2[0]);
      execlp("grep","grep","ls", NULL);
   }
//Parent do a third fork to execute wc
   else if (fork() == 0){
      dup2(fd2[0], 0);//redirect stdin of wc
      close(fd1[0]);
      close(fd1[1]);
      close(fd2[1]);
      execlp("wc","wc", NULL);
   }
//Now the parent waits for three children
   close(fd1[0]);
   close(fd1[1]);
   close(fd2[0]);
   close(fd2[1]);
   for(int i=0;i<3;i++)
      wait(NULL);
   printf("Parent is done with the three children...\n");
   return 0;
}
```
- In the above example:
    * Parent process creates two pipes
    * Parent process then creates `man` child process, setting PPFDT `1` to point to `fd1[1]`
    * Parent process then creates `grep` child process, setting PPFDT `0` to point to `fd1[0]` and `1` to point to `fd2[1]`
    * Parent process then creates `wc` child process, setting PPFDT `0` to point to `fd2[0]`
