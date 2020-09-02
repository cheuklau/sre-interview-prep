# Lecture 8

## How a C Program Starts and Terminates

1. User executes binary on terminal
2. `fork()` creates a copy of the parent
3. Child process calls `exec()` to load binary program into address space of that process
4. C startup routines:
    * Various dynamic libraries from other processes are mapped to the memory map of this process
    * Set the command line arguments, environemnt variables in the process stack
5. Main function is called
    * Calls other user defined functions which returns back to it
6. Finally either:
    * Main or user function calls exit function call
7. Exit function call performs the following before terminating the process:
    * Calls standard I/O cleanup routine which flushes I/O buffer and closes open files
    * Calls exit handlers
        + User supplied functions
8. Process terminates and returns exit code to parent
    * Note: if program uses `_exit()` to exit the program then the exit handlers (`atexit()`) are not called

## Example

- `cat prog1.c`
```
#include <stdio.h>
void display(char* msg){
    printf("%s\n",msg);
}
int main(){
    display("Learning is fun with Arif");
    return 54;
}
```
- `gcc prog1.c`
- `./a.out` to execute
- `strace ./a.out` to monitor system calls made by a process and the signals sent to it
```
execve("./a.out", ["./a.out"], [/* 45 vars */]) = 0 # Exec call with 0 as the return statement
... other system calls
brk(0x55555777000) = 0x55555777000 # Sets the heap
write(1, "Learning is fun with Arif\n", 26Learning is fun with Arif) = 26 # Converts the printf library to the write system call (file descriptor 1 is to stdout)
exit(54)
```
- Memory map different shared objects into this process's address space
- `echo $?` will show `54`

## Exit Function

- Sample program that uses `atexit` exit handler:
```
#include <stdio.h> // for perror function
#include <stdlib.h> // for exit and atexit function
#include <unistd.h> // for _exit system call

void exit_handler(){
    printf("Exit handler\n")
}
int main(){
    atexit(exit_handler);
    printf("Main is done!\n");
    return 0; // or exit(0);
}
```
- `gcc atexit_ex1.c`
- `./a.out`
```
Main is done!
Exit handler
```
- For more than one exit handler, they are executed in reverse order in which they are registered with `atexit()`

## How a C Program Terminates

- Normal termination
    * Main function's `return` statement
    * Any function calling `exit()` library call
    * Any function calling `_exit()` system call
- Abnormal termination
    * Calling `abort()` function
    * Terminated by a signal

## Limitations of atexit()

- An exit handler doesn't know what exit status was passed to `exit()`
    * This may be useful e.g., we may like to perform different actions depending on whether the process is exiting successfully
- We can't specify an argument to exit handler when called

## Library Call on_exit()

- `int on_exit(void(*func) (int, void*), void*arg)`
- `on_exit()` is also used to register exit handlers like `atexit()` but is more powerful
- Accepts two arguments: function pointer and a void pointer
- `func` is a function pointer that is passed two arguments (integer and a `void*`)
- First argument to `func` is the integer value passed to `exit()`
- Second argument is second argment to `on_exit()`

## Process Resource Limits

- Every process has a set of resource limits that can be used to restrict the amounts of various system resources that the process may consume
- We can set the resource limits of the shell using the `ulimit` built-in command
    * These limits are inherited by the processes that the sshell creates to execute user comjmands
- Since kernel 2.6.24, Linux-specific `/proc/PID/limits` file can be used to view all of the resource limits of any process
- Example: `cat /proc/2/limits`
```
Limit              Soft Limit    Hard Limit    Units
Max cpu time       unlimited     unlimited     seconds   # Max cpu time in seconds that can be used by a process
Max file size      unlimited     unlimited     bytes
Max data size      unlimited     unlimited     bytes
Max stack size     8388608       unlimited     bytes
Max processes      12017         12017         processes # Max number of child processes a parent can create
Max open files     1024          1024          files     # Max number of files a process can open at one time
Max address space  unlimited     unlimited     bytes
Max nice priority  0             0
etc
```
- Cannot increase soft limit above hard limit
- `ulimit -a` shows default limits