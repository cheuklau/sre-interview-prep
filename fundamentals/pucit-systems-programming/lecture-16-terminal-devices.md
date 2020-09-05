# Lecture 16

## In Unix everything is a file

- Seven file types:
    * Regular
    * Directory
    * Symbollic links
    * Character special files
    * Block special files
    * Named pipes
    * Sockets
- Character special files
    * Represents hardware devices that reads or writes a serial stream of data bytes
    * Devices connected via serial/parllel ports fall in this category
    * Examples: terminal devices, sound cards, tape drives
- Block special files
    * Represents hardware devices that reads or writes data in fixed size blocks
    * Provide random access to data stored on the device
    * Examples: HDD, SSD, CD-rom

## Similarities between devices and regular files

- For a process, a terminal is a source/destination of data
- Process can read from terminal device e.g., keyboard via `read()` system call or `getchar()`/`scanf()` library calls
- Process can write on terminal device via `write()` system call or `putchar()`/`printf()` library calls
- Terminal driver allows process to interact with device without knowing much of the details
- Another example is a sound card which is a source/destination of data
    * From process point of view sounds card is a file it can read/write from/to
    * Sound card encodes sound waves from microphone and sends it to the driver program which transforms the encoded data and sends it back to the process

## Overview of device files

- Terminal or `tty` driver has two buffers associated with it:
    1. input queue: holds the characters that have been received by keyboard but not yet give to the process
        * Transmitted to process only when user presses enter key
    2. output queue: holds the characters written by the process but not yet transmitted to the display unit
        * Displayed when kernel is free and has time

## Difference between device and regular files

- Regular file is a container while a device file is a connection
- The inode bock of a regular file contains pointer that points to its data blocks while the inode of a device file contains pointer that points to a function inside the kernel called the device driver
- When you see the long listing, a regular file shows its size while a device file displays the major and minor number of the device driver at the place of size when you see its long listing
- Device numbers:
    * Linux identify devices using a 16 bit number divided into two parts:
        1. Major number (8 bits) that identifies the driver program
        2. Minor number (8 bits) that is used by the driver program to identify the instance

## Proof of concepts on Linux terminal

- `sudo mknod -m 644 mychfile c 555 1`
    * `c` = character special file
    * `555` = major number
    * `1` = minor number
- `sudo mknod -m 644 myblockfile b 666 1`
- `ls -li`
```
2099788 brw-r--r-- 1 root root 666, 1 Mar 9 11:01 myblockfile
2099787 crw-r--r-- 1 root root 555, 1 Mar 9 11:00 mychfile
```
- Major table where each entry points to the device driver function of that device
- Note you cannot copy a device file
- Removing the device file will remove the entry from the directory but will not remove the device entry
- `ls -l /dev/ | grep sda` to see SCSI devices
```
brw-rw---- 1 root disk 9, 0 Jan 20 07:29 sda
```
- `ls -l /dev/ | grep tty` to see terminal devices
```
crw--w---- 1 root tty 4, 46 Jan 20 07:29
```
- `ls -l /dev/pts`` to see pseudoterminals
```
crw--w---- 1 arif tty 136, 0 Mar 9 11:04 0
crw--w---- 1 arif tty 136, 1 Mar 9 10:05 1
```
- If you open another terminal, another line will pop up with incremented value
- `tty` to show file associated with current terminal
```
/dev/pts/tty1
```
- `cp <file> /dev/pts/3` will copy the file to the terminal and display it
- Program
```
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
   if (argc != 2 ){
	fprintf(stderr,"usage: ./a.out ttyname\n");
	exit(1);
   }
   // Open file in write mode
   int fd = open(argv[1], 1);
   if (fd == -1){
	perror("open() failed");
        exit(1);
   }
   char	buf[512];	/* loop until EOF on input */
   while(fgets(buf, 512, stdin) != NULL )
      if (write(fd, buf, strlen(buf)) == -1 )
	break;
   close(fd);
   return 0;
}
```

## Modes of Terminal Driver

- Canonical mode
    * Input is made available line by line and the line goes to the process only after the user presses the Enter key
        * Meanwhile it is buffered inside the `tty` driver program
    * Line editing is enabled
- Non-canonical mode
    * Input is made immediately available as a key is pressed without the need to press the Enter key
        * No buffering is done by the driver program
    * Line editing is disabled

## Attributes of Terminal Driver

- Actions performed by `tty` driver on the data passing through it can be grouped into four main categories:
    1. Input processing
        * Processing performed by `tty` driver on characters received via keyboard before sending them to the process e.g., `icrnl`
    2. Output processing
        * Processing performed by `tty` driver on characters received from process before sending them to the display unit e.g., `onlcr`
    3. Control processing
        * How many characters are represented e.g., `cs8`
    4. Local processing
        * What the driver does while the characters are inside the driver e.g., `icanon`, `echo`
- How can we examine and modify terminal attributes?
    * `stty` can be used to examine and modify terminal attributes
- Simple program to get character, print on stdout:
```
#include <stdio.h>
#include <ctype.h>

int main()
{
    int ch;
    while ((ch = getchar()) != EOF){
        putchar(ch);
    }
}
```

## Programming the terminal driver

- There are three ways you can get/set the attributes of the terminal driver inside C program:
    1. `system()` library call
    2. `tcgetattr()` and `tcsetattr()` library calls
    3. `ioctl()` system call
- `system()` library call
    * `int system(const char* command);`
    * Executes a command specified in `cmd` by calling `/bin/bash -c <command>` and returns after command has been completed
    * Return `-1` on error and return status of the command otherwise
    * Main cost of `system()` is inefficiency
        + Executing a command using `system()` requires creation of at least two processes:
            - One for the shell
            - One for the command(s) it executes
- Example program that gets a password and compares it to a value:
```
#include <stdio.h>
#include <termios.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
	char passwd[50];
	printf("Password:");
    // primpt user for a password
	fgets(passwd, 50, stdin);
//the passwd contains the string entered by user + '\n' and then '\0', we need to remove the '\n' if there is any
	char *q;
   q = strchr(passwd, '\n');
   *q = '\0';
	int rv = strcmp(passwd, "pucit");
	if (rv == 0)
		printf("\nThe password is correct\n");
	else
		printf("\nThe password is incorrect\n");

	return 0;

}
```
- Example above except we use `system()` to disable `echo` via `stty` so that password not displayed to terminal when being entered
```
#include <stdio.h>
#include <termios.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
   char passwd[50];
   printf("Password:");
//make the echo attribute off using stty command
   system("stty -echo");
	fgets(passwd, 50, stdin);
	char *q;
   q = strchr(passwd, '\n');
   *q = '\0';
//make the echo attribute on using stty command
	system("stty echo");
	int rv = strcmp(passwd, "pucit");
	if (rv == 0)
		printf("\nThe password is correct\n");
	else
		printf("\nThe password is incorrect\n");
	return 0;
}
```
- `tcgetattr()` and `tcsetattr()` library calls
    * `int tcgetattr(int fd, struct termios* info);`
    * `int tcsetattr(int fd, int when, struct termios* info)`
    * `tcgetattr()` copies current settings from `tty` driver associated to the open file `fd` into struct pointed by `info`
        + Returns `0` on success and `-1` on error
    * `tcsetattr()` sets `tty` driver associated to the open file `fd` with the settings given in the struct pointed by `info`
        + `when` argument tells when to update driver settings, and can take following values:
            - `TCSANOW`: update driver settings immediately
            - `TCSADRAIN`: wait until all output already queued in the driver has been transmitted to the terminal and then update the driver
            - `TCSAFLUSH`: wait for output queue to be emptied and flush all queued input data and then update the driver
- Program:
```
#include <stdio.h>
#include <termios.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
	char passwd[50];
	printf("Password:");
//get attributes
   struct termios info;
   tcgetattr(0, &info);
//save a copy of original attributes
   struct termios save = info;
//make the echo bit off and set attributes
   info.c_lflag &= ~ECHO;
   tcsetattr(0, TCSANOW, &info);
//get password from user
   fgets(passwd, 50, stdin);
   char *q;
   q = strchr(passwd, '\n');
   *q = '\0';
//now set the attributes back to original
   tcsetattr(0, TCSANOW, &save);
//compare password and print appropriate message
   int rv = strcmp(passwd, "pucit");
   if (rv == 0)
		printf("\nThe password is correct\n");
	else
		printf("\nThe password is incorrect\n");
	return 0;
}
```
- Three steps to change the attributes of a terminal driver:
    1. Get attributes from the driver
    2. Modify the attributes you need to change
    3. Send revised attributes back to the driver
- `ioctl()` system call
    * `int ioctl(int fd, int request[,arg,...]);`
    * We have seen the use of `fcntl()` system call to get/set attributes of a disk file
    * To get/set attributes of device files we can use the `ioctl()` system call
    * Each type of device has its own set of properties and `ioctl` operations
    * First arguement `fd` specifies an open file descriptior that refers to a device
    * Second argument `request` specifies the control function to be performed based upon the device being addressed
        * Defined in `/usr/include/asm-generic/ioctls.h`
    * Remaining optional arguments are request specific, defined in `/usr/include/x86_64-linux-gnu/bits/ioctl-types.h`
- Example to turn on the echo flag in the `c_lflag` member of `termios` structure using `ioctl()`:
```
struct termios info;
ioctl(0, TCGETS, &info);
info.c_lflag = info.c_lflag | ECHO;
ioctl(0, TCGETS, &info);
```
- Program:
```
#include <stdio.h>
#include <termios.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
int main(int argc, char *argv[])
{
	char passwd[50];
	printf("Password:");
//get attributes
        struct termios info;
        ioctl(0,TCGETS, &info);
//save a copy of original attributes
	struct termios save = info;
//make the echo bit off and set attributes
        info.c_lflag &= ~ECHO;
        ioctl(0, TCSETS, &info);
//get password from user
	fgets(passwd, 50, stdin);
	char *q;
   q = strchr(passwd, '\n');
   *q = '\0';
//now set the attributes back to original
	ioctl(0, TCSETS, &save);
//compare password and print appropriate message
	int rv = strcmp(passwd, "pucit");
	if (rv == 0)
		printf("\nThe password is correct\n");
	else
		printf("\nThe password is incorrect\n");
	return 0;
}
```
- Another example for getting the screen size using `ioctl()`