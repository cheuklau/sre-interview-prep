# Lecture 27

## Introduction to FIFOs

- Pipes have no names and their biggest disadvantage is that they can be only used between processes that have a parent process in common (ignoring descriptor passing)
- Unix FIFO is similar to a pipe as it is a one way flow of data
    * Unlike pipes, FIFO has a path name associated with it allowing unrelated processes to access a single pipe
- FIFOs (a.k.a named pipes) are used for communication between related or unrelated processes executing on the same machine
- FIFO is created by one process and can be opened by multiple processes for reading or writing
    * When processes are reading or writing data via FIFO, kernel passes all data internally without writing it to the file system
    * Thus, FIFO file has no contents on the file system
    * File system entry merely serves as a reference point so that processes can access the pipe using a name in the file system

## Use of FIFO between unrelated processes

- Assume we have created a FIFO file on the hard disk `fifo1`
- Process 1: `echo "Hello Pucit" 1> fifo1`
    * Kernel redirects writing to FIFO file to a kernel buffer inside its own memory created for that FIFO
- Process 2: `cat fifo1`
    * Kernel redirects reading from FIFO file to a kernel buffer inside its own memory created for that FIFO
- Note: FIFO is process persistent and name is file system persistent
- `man 7 fifo` similar to a pipe but accesses as part of filesystem
- `mkfifo` or `mknod` can be used to create fifos
- `mkfifo fifo1`
- `mknod fifo2`
- Note: `fifo1` and `fifo2` will have type `p` when you type `ls -l`
- `echo "hello" 1> fifo1` will be blocked because no reader on the other side
- `cat fifo2` will also be blocked because it is an empty fifo
- Create two terminals
    * Terminal 1: `echo "hello" 1> fifo1`
    * Terminal 2: `cat fifo1`
        + This will retrieve `hello`
- Example of bash script file that creates a fifo
```
#!/bin/bash
while true
do
  rm -f /tmp/time_fifo
  mkfifo /tmp/time_fifo
  sleep 1
  date 1> /tmp/time_fifo
done
```
- We run `cat /tmp/time_fifo` to read fifo file from above example

## mkfifo() library call

- `int mkfifo(const char*pathname, mode_t mode);`
- Makes a FIFO special file with name `pathname`
    * Second argument `mode` specifies the FIFO's permissions
    * Modified by process's `umask` in the usual way
- Once you have created a FIFO, any process can open it for reading or writing in the same way as an ordinary file
    * Opening a FIFO for reading normally blocks until some other process opens the same FIFO for writing and vice versa
- Call fails when:
    * Parent directory does not allow write permission
    * Path name already exists
    * Path name points outside accessible address space
    * Path name too long
    * Insufficient kernel memory

## mknod() system call

- `int mknod(const char*name, mode_t mode, dev_t device);`
- `mknod()` system call creates a FIFO file with `name`
- Second argument `mode` specifies both the permissions to use and the type of node to be created
    * It should be a combination (using bitwise `OR`) of one of the file types (`S_IFREG`, `S_IFIFO`, `S_IFCHR`, `S_IFBLK`, `S_IFSOCK`) and the permissions for the file
- For creating a named pipe the third argument is set to zero
    * However, to create a character or block special file, we need to mention the major and minor numbers of the newly created device special file

## Example
- Writer program:
```
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
int main(){
   char buff[1024];
   // Use mknod system call to create a FIFO
   mknod("myfifo", S_IFIFO | 0666, 0);
   printf("Waiting for readers....\n");
   // Open FIFO is write only mode
   int writefd = open("myfifo", O_WRONLY);
   printf("Got a reader -- type some text to be sent\n");
   //read from stdin and write to the fifo
   while(fgets(buff, 1023, stdin))
      write(writefd, buff, strlen(buff));
   return 0;
}
```
- Reader program:
```
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
int main(){
   char buff[1024];
   int num;
   mknod("myfifo", S_IFIFO | 0666, 0);
   printf("Waiting for writers....\n");
   // Open FIFO in read only mode
   int readfd = open("myfifo", O_RDONLY);
   printf("Got a writer\n");
   do{//keep reading from myfifo
      num = read(readfd, buff, 1024);
      buff[num] = '\0';
      //display the contents on stdout
      printf("Reader read %d bytes: %s\n",num, buff);
   }while(num > 0); // read until EOF
   return 0;
}
```

## Bidirectional communication using FIFOs

- Create two FIFOs `fifo1` and `fifo2`
- Process one has `fifo1` in read mode and `fifo2` in write mode
- PRocess two has `fifo1` in write mode and `fifo2` in read mode
- Example containing process one:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/errno.h>
#define MESSAGE1 "\n\n\nThis is a message from student:\n\t This program is 2 difficult to understand sir!\n"

 int main(){
   char buff[1024];
   int readfd, writefd, n, size;
//open fifo1 for writing
   writefd = open ("/tmp/fifo1", 1);
//open fifo2 for reading
   readfd = open ("/tmp/fifo2", 0);
//Write a message in fifo1 to be sent to other process
   write(writefd, MESSAGE1, strlen(MESSAGE1) + 1);
//Read a message from fifo2
   n = read(readfd, buff, 1024);

//Writes the msg sent by other program on screen
   write(1, buff, n);
   close (readfd);
   close (writefd);
//remove fifos now that we are done using them
   if(unlink("/tmp/fifo1") <0){
	perror("Client unlink FIFO1");
	exit (1);
   }
   if(unlink("/tmp/fifo2") <0){
	perror("Client unlink FIFO2");
	exit (1);
   }
   return 0;
}
```
- Example containing process two:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/errno.h>
#define MESSAGE2 "\nResponse from Teacher: \n\tThere is no short cut to hard work! So WORK HARD....\n\n\n\n"


int main(){
   char buff[1024];
   int rv, readfd, writefd, n, size;
//create fifo1 using mknod system call
   mknod("/tmp/fifo1", S_IFIFO | 0666, 0);
//create  fifo2 using mkfifo library call
   rv = mkfifo("/tmp/fifo2", 0666);
   if(rv == -1){
	unlink("/tmp/fifo1");
	perror("mkfifo failed");
	exit(1);
	}
//Open fifo1 for reading purpose
   readfd = open ("/tmp/fifo1", 0);
//Open fifo2 for writing purpose
   writefd = open ("/tmp/fifo2", 1);
//Make a blocking call on fifo1
   n=read(readfd, buff, 1024);
//Display that message on screen
   write(1, buff, n);
//Send a response to other program via fifo2
   sleep(20);
   write(writefd, MESSAGE2, strlen(MESSAGE2) + 1);
   close (readfd);
   close (writefd);
   return 0;
}
```