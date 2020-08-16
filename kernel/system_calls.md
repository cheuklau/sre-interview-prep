# System Calls

## Introduction to System Calls

- Most common way to implement syscalls is as software interrupts

### System Call. What is it?

- A syscall is a userspace request of a kernel service
- The OS kernel provides many services
- For example, when program wants to write or read from a file, start to listen for connections on a socket, delete or create a directory, a program uses a syscall
- Syscall is just a C kernel space function that user space program calls to handle some request
- `x86_64` provides 322 syscalls, `x86` provides 358
- Example `hello world` written in assembly:
```
.data

msg:
    .ascii "Hello, world!\n"
    len = . - msg

.text
    .global _start

_start:
	movq  $1, %rax
    movq  $1, %rdi
    movq  $msg, %rsi
    movq  $len, %rdx
    syscall

    movq  $60, %rax
    xorq  %rdi, %rdi
    syscall
```
- Compile above `gcc -c test.S`
- Dynamically link `ld -o test test.o`
- Run it in user space `./test`
- `syscall` instruction jumps to the address stored in `MSR_LSTAR` (long system target address register)
- Kernel provides its own custom function for handling syscalls as well as writing the address of `MSR_LSTAR` register upon startup
- `syscall` invokes a handler of a given syscall
- Each syscall has a unique number as shown in the syscall table
- In above example, first syscall is `write` which writes data to given file
    * `write` has number `1` which is passed through `rax` register
    * The remaining three `rdi`, `rsi` and `rdx` contains remaining three parameters required by `write`
        + File descriptor (`1` stands for stdout)
        * Pointer to string
        * Size of data
- `strace test` shows the `write` and `exit` syscalls
- We do not use syscalls directly in our code. For example:
```
#include <stdio.h>

int main(int argc, char **argv)
{
   FILE *fp;
   char buff[255];

   fp = fopen("test.txt", "r");
   fgets(buff, 255, fp);
   printf("%s\n", buff);
   fclose(fp);

   return 0;
}
```
- There are no `fopen`, `fgets`, `printf` and `fclose` syscalls, but `open`, `read`, `write`, and `close` instead
- `fopen`, `fgets`, `printf` and `fclose` are defined in the C standard library
- These functions are wrappers for syscalls
- Main reason is that syscalls need to be performed quickly and the standard library makes sure that syscalls have the correct parameters and performs different checks before making the given syscall
- If we compile the program `gcc test.c -o test` and run it with `ltrace ./test` we see:
```
$ ltrace ./test
__libc_start_main([ "./test" ] <unfinished ...>
fopen("test.txt", "r")                                             = 0x602010
fgets("Hello World!\n", 255, 0x602010)                             = 0x7ffd2745e700
puts("Hello World!\n"Hello World!

)                                                                  = 14
fclose(0x602010)                                                   = 0
+++ exited (status 0) +++
```
- `ltrace` shows the userspace calls of a program
- Each program needs to open/write/read files and network connections, allocate memory and other things that can only be provided by the kernel
- `/proc/<pid>/syscall` exposes the syscall number and argument registers for syscall currently executed by the process

### Implementation of Write Syscall

- Stopped here

## How the Linux Kernel Handles a System call

## vstscall and vDSO

## How the Linux Kernel Runs a Program

## Implementation of the Open System Call

## Limits on Resources in Linux