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

- Source code of the Linux kernel `fs/read_write.c`:
```
SYSCALL_DEFINE3(write, unsigned int, fd, const char __user *, buf,
		size_t, count)
{
	struct fd f = fdget_pos(fd);
	ssize_t ret = -EBADF;

	if (f.file) {
		loff_t pos = file_pos_read(f.file);
		ret = vfs_write(f.file, buf, count, &pos);
		if (ret >= 0)
			file_pos_write(f.file, pos);
		fdput_pos(f);
	}

	return ret;
}
```
- It takes three arguments:
    1. `fd` = file descriptor
    2. `buf` = buffer to write
    3. `count` = length of buffer to write
- `write` writes data from a buffer declared by the user to a given device or file
- The functioon performs the following:
    * `fdget_pos` to convert FD numeral to the `fd` structure
    * `file_pos_read` gets the current position in the file
    * `vfs_write` writes the given buffer too the given file starting from the given position

## How the Linux Kernel Handles a System call

- Recall, we used `write` via C standard library to make the system calls `sys_write`
- Application must fill general purpose registers with correct values in order to use the syscall instruction to make the actual system call

### Initialization of the Syscall Table

- Syscalls are implemented as software interrupts
- When a processor handles a syscall instruction from a user application, the instruction causes an exception which transfers control to an exception handler
- Recall, all exception handlers are placed in the kernel code
- Kernel uses a system call table in order to find the address of the required system call handler for a specific system call
- Syscall table is represented by `sys_call_table` array in the kernel

### Skip: Initialization of the Syscall Entry

### Skip: Preparation Before syscall Handler will be Called

### Skip: Exit from a Syscall

Full path:
    1. User app conatins code that fills general purpose register with values (syscall number and arguments of syscall)
    2. Processor switches from user mode to kernel mode and starts execution of syscall entry `entry_SYSCALL_64`
    3. `entry_SYSCALL_64` switches to the kernel stack and saves some general purpose registers, old stack and code segment, flags, etc onto the stack
    4. `entry_SYSCALL_64` checks syscall number in `rax` register, searches syscall handler in `sys_call_table` and calls it
    5. After syscall handler finishes its work, restores general purpose registers, old stack, flags and return address and exit from `entry_SYSCALL_64` with `sysretq` instruction

## vsyscall and vDSO

- vsyscall and vdso designed to speed up process for making syscalls

### Introduction to vsyscalls

- `vsyscall` allows kernel to map into user space a page that contains some variables and implementation of certain syscalls
- These syscalls can then be executed in userspace without having to context switch

### Introduction to vDSO

- `vdso` (virtual dynamic shared object) replaces `vsyscall`
- `vdso` maps memory pages into each process in a shared object form, but `vsyscall` is static in memory and has the same address each time
- All userspace apps that dynamically link to `glibc` will use `vdso` automatically

## How the Linux Kernel Runs a Program

### How Do we Launch Our Programs?

- Consider running `ls` in a `bash` shell:
    * Assume `bash` already started and is in `reader_loop` function waiting to read and execute commands
    * `reader_loop` makes all checks, reads the given program name and argument then calls the `execute_command` function
    * `execute_command` function performs checks e.g., do we need to start `subshell`, etc
    * At the end `execute_command` runs `shell_execve` function which calls the `execve` system call which executes a program by the given filename with the given arguments and environment variables
        + If we did an `strace ls` we will see `execve("/bin/ls", ["ls"], [/* 62 vars */])=0`

### execve system call

- `execve` calls `do_execve` which does the following:
    + Initialize two pointers oon userspace data with the given arguments and environment variables
    + Returns the result of `do_execveat_common` which actually executes the program:
        * Calls `sched_exec` functioon to determine least loaded processor to execute the new program
        * Check file descriptor of the executable binary
        * Calls `bprm_mm_init` initializes memory descriptor i.e., `mm_struct` which represents address space of a process
        * Call `exec_binrpm` storing pid, and call `search_binary_handler` which goes through list oof handlers to find the binary format e.g., `binfmt_script` for interpreted scripts starting from the `#!` line, `binfmt_misc` for different binary formats, etc
        * Call `start_thread` with:
            + Set of registers for the new task
            + Address of entry point of new task
            + Address of top of stack for new task
        * Return from `exec_binrpm` back to `do_execveat_common` which will release memory for structures
        * After returning from `execve` syscall handler, execution of program starts
        * Note that `execve` syscall does not return control to a process, but code, data and other segments of the caller process are overwritten
        * `exit` syscall used when app exits

## Skipped: Implementation of the Open System Call

## Limits on Resources in Linux

- Three fundamental sysaxlls to manage resource limit for a process
    1. `getrlimit` - process read limits on a system resource
    2. `setrlimit` - process set limit on system resource
    3. `prlimit` - extension of previous functions based on pid
- Two types of limits
    1. `soft` - actual limit for a resource of a process
    2. `hard` - ceiling value of a `soft` limit only set by superuser
- `prlimit` is used by `ulimit` utility
- `strace ulimit` will shoow calls to `prlimit`
- Available resources:
    * `RLIMIT_CPU` - CPU time in seconds
    * `RLIMIT_FSIZE` - max file size
    * `RLIMIT_DATA`
    * `RLIMIT_STACK` - max size of process stack in bytes
    * `RLIMIT_CORE`
    * `RLIMIT_RSS` - number of bytes allocaoted in RAM
    * `RLIMIT_NPROC` - max processes created by user
    * etc